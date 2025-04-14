<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        getEmailsMarkedTemplate,
        getEmailsUnmarkedTemplate,
        getErrorCopyEmailsTemplate,
        getErrorMarkEmailsTemplate,
        getErrorMoveEmailsTemplate,
        getErrorUnmarkEmailsTemplate,
        getNotImplementedTemplate,
    } from "$lib/templates";
    import { type Email, Mark, Folder, type Mailbox } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import * as Context from "$lib/ui/Components/Context";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import {
        isStandardFolder,
        isUidInSelection,
        simpleDeepCopy,
        sortSelection,
    } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    type GroupedUidSelection = [string, string][];
    type GroupedMessageIdSelection = [string, string[]][];

    interface Props {
        emailSelection: "1:*" | string[];
        currentOffset: number;
    }

    let { emailSelection = $bindable([]), currentOffset = $bindable() }: Props =
        $props();

    let inCustomFolder = $derived.by(() => {
        if (SharedStore.currentAccount == "home") return false;

        return SharedStore.folders[
            SharedStore.currentAccount.email_address
        ].custom.includes(getCurrentMailbox().folder);
    });

    let groupedEmailSelection: GroupedUidSelection = $derived.by(() => {
        if (!emailSelection) return [];

        const accountUidMap: Record<string, string> = {};
        // When the `emailSelection` will be something like this:
        // ["account1@mail.com,123", "account1@mail.com,124", "account2@mail.com,123"]
        // so `groupedEmailSelection` will be something like this:
        // [["account1@mail.com", "123,124"], ["account2@mail.com", "123"]]
        // and with this way, we are minimizing api calls from this:
        // C: A101 +STORE FLAG account1@mail.com 123
        // C: A102 +STORE FLAG account1@mail.com 124
        // C: A103 +STORE FLAG account1@mail.com 125
        // to this:
        // C: A101 +STORE FLAG account1@mail.com 123, 124
        // C: A102 +STORE FLAG account1@mail.com 125
        if (emailSelection === "1:*") {
            if (SharedStore.currentAccount === "home") {
                SharedStore.accounts.forEach((account) => {
                    accountUidMap[account.email_address] = "1:*";
                });
            } else {
                accountUidMap[SharedStore.currentAccount.email_address] = "1:*";
            }
        } else {
            emailSelection.forEach((selection) => {
                const [emailAddr, uid] = selection.split(",");
                accountUidMap[emailAddr] = Object.hasOwn(
                    accountUidMap,
                    emailAddr,
                )
                    ? accountUidMap[emailAddr].concat(",", uid)
                    : uid;
            });
        }
        return Object.entries(accountUidMap);
    });

    let selectShownCheckbox: HTMLInputElement;
    let shownEmailUids: string[] = [];
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    $effect(() => {
        if (getCurrentMailbox()) {
            shownEmailUids = [];
            document
                .querySelectorAll<HTMLInputElement>(
                    ".mailbox .email-selection-checkbox",
                )
                .forEach((element) => {
                    shownEmailUids.push(element.value);
                });
        }
    });

    function isSelectedEmailsHaveUnsubscribeOption() {
        return groupedEmailSelection.every((group) => {
            const emailAddress = group[0];
            const uids = group[1].split(",");
            const targetMailbox =
                SharedStore.mailboxes[emailAddress].emails.current;
            return uids.every((uid) =>
                targetMailbox.find(
                    (email) => email.uid == uid && !!email.list_unsubscribe,
                ),
            );
        });
    }

    function isSelectedEmailsIncludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((selection) => {
            const [emailAddress, uid] = selection.split(",");
            return SharedStore.mailboxes[emailAddress].emails.current.find(
                (email: Email) =>
                    email.uid == uid &&
                    Object.hasOwn(email, "flags") &&
                    email.flags!.includes(mark),
            );
        });
    }

    function isSelectedEmailsExcludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((selection) => {
            const [emailAddress, uid] = selection.split(",");
            return SharedStore.mailboxes[emailAddress].emails.current.find(
                (email: Email) =>
                    email.uid == uid &&
                    Object.hasOwn(email, "flags") &&
                    !email.flags!.includes(mark),
            );
        });
    }

    function getMessageIdsOfSelection(
        selection: GroupedUidSelection,
    ): GroupedMessageIdSelection {
        let foundSelection: Record<string, string[]> = {};
        selection.map((group) => {
            const emailAddress = group[0];
            const uids = group[1].split(",");
            foundSelection[emailAddress] = [];
            uids.forEach((uid) => {
                const email = SharedStore.mailboxes[
                    emailAddress
                ].emails.current.find((em) => em.uid === uid);
                if (email) {
                    foundSelection[emailAddress].push(email.message_id);
                }
            });
            return;
        });
        return Object.entries(foundSelection);
    }

    async function getNewUidsByMessageId(
        selection: GroupedMessageIdSelection,
        folder: string,
    ): GroupedUidSelection {
        const foundSelection: GroupedUidSelection = [];
        const results = await Promise.allSettled(
            selection.map(async (group) => {
                const emailAddress = group[0];
                const messageIds = group[1];
                const response = await MailboxController.searchEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    folder,
                    { message_id: messageIds },
                );
                if (!response.success || !response.data) {
                    throw new Error(response.message);
                }
                const foundUids = response.data[emailAddress].join(",");
                foundSelection.push([emailAddress, foundUids]);
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({ title: "asdad" });
            failed.forEach((f) => console.error(f.reason));
        }

        return foundSelection;
    }

    async function markEmails(mark: string | Mark, isUndo: boolean = false) {
        const currentSelection = simpleDeepCopy(groupedEmailSelection);
        const results = await Promise.allSettled(
            groupedEmailSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.markEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    mark,
                    getCurrentMailbox().folder,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: getErrorMarkEmailsTemplate(mark),
            });
            failed.forEach((f) => console.error(f.reason));
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: getEmailsMarkedTemplate(mark),
                onUndo: () => {
                    groupedEmailSelection = currentSelection;
                    unmarkEmails(mark, true);
                },
            });
        }
    }

    async function unmarkEmails(mark: string | Mark, isUndo: boolean = false) {
        const currentSelection = simpleDeepCopy(groupedEmailSelection);
        const results = await Promise.allSettled(
            groupedEmailSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.unmarkEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    mark,
                    getCurrentMailbox().folder,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: getErrorUnmarkEmailsTemplate(mark),
            });
            failed.forEach((f) => console.error(f.reason));
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: getEmailsUnmarkedTemplate(mark),
                onUndo: () => {
                    groupedEmailSelection = currentSelection;
                    markEmails(mark, true);
                },
            });
        }
    }

    const selectEmail = (e: Event) => {
        if (emailSelection === "1:*") return;
        const selectedEmail = e.target as HTMLElement;
        const selectedEmailUid = selectedEmail.querySelector<HTMLInputElement>(
            ".email-selection-checkbox",
        )!.value;
        emailSelection.push(selectedEmailUid);
    };

    const deselectEmail = (e: Event) => {
        if (emailSelection === "1:*") return;
        const selectedEmail = e.target as HTMLElement;
        const selectedEmailUid = selectedEmail.querySelector<HTMLInputElement>(
            ".email-selection-checkbox",
        )!.value;
        emailSelection = emailSelection.filter(
            (selection) => selection !== selectedEmailUid,
        );
    };

    const selectShownEmails = (event: Event) => {
        emailSelection = selectShownCheckbox.checked ? shownEmailUids : [];
    };

    const copyTo = async (
        selection: GroupedUidSelection,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        isUndo: boolean = false,
    ): Promise<void> => {
        const currentSelection = simpleDeepCopy(selection);
        const messageIdsOfSelection =
            getMessageIdsOfSelection(currentSelection);

        const undo = async () => {
            const newUids = getNewUidsByMessageId(
                messageIdsOfSelection,
                destinationFolder,
            );
            await deleteFrom(newUids, destinationFolder, true);
        };

        const results = await Promise.allSettled(
            currentSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.copyEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    sourceFolder,
                    destinationFolder,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_move_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const moveTo = async (
        selection: GroupedUidSelection,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        isUndo: boolean = false,
    ): Promise<void> => {
        const currentSelection = simpleDeepCopy(selection);
        const messageIdsOfSelection =
            getMessageIdsOfSelection(currentSelection);

        const undo = async () => {
            const newUids = getNewUidsByMessageId(
                messageIdsOfSelection,
                destinationFolder,
            );
            await moveTo(newUids, destinationFolder, sourceFolder, true);
        };

        const results = await Promise.allSettled(
            currentSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.moveEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    sourceFolder,
                    destinationFolder,
                    isUndo ? undefined : currentOffset,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_move_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const deleteFrom = async (
        selection: GroupedUidSelection,
        folder: string | Folder,
        isUndo: boolean = false,
    ): Promise<void> => {
        const currentSelection = simpleDeepCopy(selection);
        const messageIdsOfSelection =
            getMessageIdsOfSelection(currentSelection);

        const undo = async () => {
            const newUids = getNewUidsByMessageId(
                messageIdsOfSelection,
                Folder.Trash,
            );
            await moveTo(newUids, Folder.Trash, folder, true);
        };

        const results = await Promise.allSettled(
            currentSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.deleteEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    folder,
                    isUndo ? undefined : currentOffset,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_delete_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else if (!isStandardFolder(folder, Folder.Trash)) {
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const unsubscribe = async () => {
        // Since "unsubscribe/reply/forward" options are disabled when there is
        // more than one current account("home"), groupedEmailSelection's length
        // isn't going to be more than 1, so first index is enough to cover
        // selection.
        if (emailSelection.length > 1) return;

        const emailAddress = groupedEmailSelection[0][0];
        const uid = groupedEmailSelection[0][1];
        const email = SharedStore.mailboxes[emailAddress].emails.current.find(
            (em) => em.uid == uid,
        )!;

        if (!email.list_unsubscribe) return;

        const response = await MailboxController.unsubscribe(
            SharedStore.accounts.find(
                (account) => account.email_address === emailAddress,
            )!,
            email.list_unsubscribe,
            email.list_unsubscribe_post,
        );

        if (!response.success) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
        }

        showToast({ content: "Unsubscribe success" });
    };

    const unsubscribe_all = async () => {
        const currentSelection = simpleDeepCopy(groupedEmailSelection);
        const results = await Promise.allSettled(
            currentSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = group[1];

                const account = SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!;

                const emails = SharedStore.mailboxes[
                    emailAddress
                ].emails.current.filter((email) => {
                    return (
                        isUidInSelection(uids, email.uid) &&
                        email.list_unsubscribe
                    );
                });

                const unsubscribeResultOfAccount = await Promise.allSettled(
                    emails.map(async (email) => {
                        const response =
                            await MailboxController.unsubscribe(
                                account,
                                email.list_unsubscribe!,
                                email.list_unsubscribe_post,
                            );

                        if (!response.success) {
                            throw new Error(response.message);
                        }
                    }),
                );

                const failed = unsubscribeResultOfAccount.filter(
                    (r) => r.status === "rejected",
                );
                if (failed.length > 0) {
                    failed.forEach((f) => console.error(f.reason));
                    throw new Error("one or more unsubscribe operations have failed.");
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        showToast({ content: "success unsubscribe" });
    };

    const reply = async () => {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;

        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const replyingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((email) => email.uid == replyingEmailUid)!;

        showContent(Compose, {
            originalMessageContext: {
                composeType: "reply",
                originalMessageId: email.message_id,
                originalSender: email.sender,
                originalReceiver: email.receivers,
                originalSubject: email.subject,
                originalBody: email.body,
                originalDate: email.date,
            },
        });
    };

    const forward = async () => {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;

        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const forwardingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((email) => email.uid == forwardingEmailUid)!;

        showContent(Compose, {
            originalMessageContext: {
                composeType: "forward",
                originalMessageId: email.message_id,
                originalSender: email.sender,
                originalReceiver: email.receivers,
                originalSubject: email.subject,
                originalBody: email.body,
                originalDate: email.date,
            },
        });
    };

    const refresh = async (): Promise<void> => {
        const accounts =
            SharedStore.currentAccount !== "home"
                ? [SharedStore.currentAccount]
                : SharedStore.accounts;

        const results = await Promise.allSettled(
            accounts.map(async (account) => {
                const response = await MailboxController.getMailbox(account);
                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({
                title: local.error_refresh_mailbox_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
        }
    };
</script>

<Context.Root
    target=".mailbox .email"
    beforeOpen={selectEmail}
    afterClose={deselectEmail}
>
    {#if !isSelectedEmailsIncludesGivenMark(Mark.Flagged)}
        <Context.Item
            onclick={async () => {
                await markEmails(Mark.Flagged);
            }}
        >
            {local.star[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Flagged)}
        <Context.Item
            onclick={async () => {
                await unmarkEmails(Mark.Flagged);
            }}
        >
            {local.remove_star[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item
            onclick={async () => {
                await markEmails(Mark.Seen);
            }}
        >
            {local.mark_as_read[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item
            onclick={async () => {
                await unmarkEmails(Mark.Seen);
            }}
        >
            {local.mark_as_unread[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if emailSelection.length == 1}
        <Context.Separator />
        <Context.Item onclick={reply}>
            {local.reply[DEFAULT_LANGUAGE]}
        </Context.Item>
        <Context.Item onclick={forward}>
            {local.forward[DEFAULT_LANGUAGE]}
        </Context.Item>
        <Context.Separator />
        <Context.Item onclick={unsubscribe}>
            {local.unsubscribe[DEFAULT_LANGUAGE]}
        </Context.Item>
    {:else if isSelectedEmailsHaveUnsubscribeOption()}
        <Context.Item onclick={unsubscribe_all}>
            {local.unsubscribe_all[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    <Context.Separator />
    {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
        <Context.Item
            onclick={async () => {
                await moveTo(
                    groupedEmailSelection,
                    Folder.Archive,
                    Folder.Inbox,
                );
            }}
        >
            {local.move_to_inbox[DEFAULT_LANGUAGE]}
        </Context.Item>
    {:else}
        <Context.Item
            onclick={async () => {
                await moveTo(
                    groupedEmailSelection,
                    getCurrentMailbox().folder,
                    Folder.Archive,
                );
            }}
        >
            {local.move_to_archive[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    <Context.Item
        onclick={async () => {
            await deleteFrom(groupedEmailSelection, getCurrentMailbox().folder);
        }}
    >
        {isStandardFolder(getCurrentMailbox().folder, Folder.Trash)
            ? local.delete_completely[DEFAULT_LANGUAGE]
            : local.delete[DEFAULT_LANGUAGE]}
    </Context.Item>
</Context.Root>

<div class="toolbox-left">
    <div class="tool">
        <Input.Basic
            type="checkbox"
            id="select-shown"
            onclick={selectShownEmails}
        />
    </div>
    {#if emailSelection.length > 0}
        {#if !isSelectedEmailsIncludesGivenMark(Mark.Flagged)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await markEmails(Mark.Flagged);
                    }}
                >
                    {local.star[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsExcludesGivenMark(Mark.Flagged)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await unmarkEmails(Mark.Flagged);
                    }}
                >
                    {local.remove_star[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsIncludesGivenMark(Mark.Seen)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await markEmails(Mark.Seen);
                    }}
                >
                    {local.mark_as_read[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await unmarkEmails(Mark.Seen);
                    }}
                >
                    {local.mark_as_unread[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await moveTo(
                            groupedEmailSelection,
                            Folder.Archive,
                            Folder.Inbox,
                        );
                    }}
                >
                    {local.move_to_inbox[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {:else}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={async () => {
                        await moveTo(
                            groupedEmailSelection,
                            getCurrentMailbox().folder,
                            Folder.Archive,
                        );
                    }}
                >
                    {local.move_to_archive[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={async () => {
                    await deleteFrom(
                        groupedEmailSelection,
                        getCurrentMailbox().folder,
                    );
                }}
            >
                {isStandardFolder(getCurrentMailbox().folder, Folder.Trash)
                    ? local.delete_completely[DEFAULT_LANGUAGE]
                    : local.delete[DEFAULT_LANGUAGE]}
            </Button.Action>
        </div>
        {#if groupedEmailSelection.length == 1}
            {@const emailAddress = groupedEmailSelection[0][0]}
            <div class="tool-separator"></div>
            <div class="tool">
                <Select.Root
                    onchange={async (destinationFolder) => {
                        await copyTo(
                            groupedEmailSelection,
                            getCurrentMailbox().folder,
                            destinationFolder,
                        );
                    }}
                    placeholder={local.copy_to[DEFAULT_LANGUAGE]}
                >
                    {#if inCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                    {#each SharedStore.folders[emailAddress].custom as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== getCurrentMailbox().folder}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                </Select.Root>
            </div>
            <div class="tool">
                <Select.Root
                    onchange={async (destinationFolder) => {
                        await moveTo(
                            groupedEmailSelection,
                            getCurrentMailbox().folder,
                            destinationFolder,
                        );
                    }}
                    placeholder={local.move_to[DEFAULT_LANGUAGE]}
                >
                    {#if inCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                    {#each SharedStore.folders[emailAddress].custom as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== getCurrentMailbox().folder}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                </Select.Root>
            </div>
        {/if}
    {:else}
        <div class="tool">
            <Button.Action type="button" class="btn-inline" onclick={refresh}>
                {local.refresh[DEFAULT_LANGUAGE]}>
            </Button.Action>
        </div>
    {/if}
</div>
