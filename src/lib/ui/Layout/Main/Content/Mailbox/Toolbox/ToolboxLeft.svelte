<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
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
    import {
        isStandardFolder,
        isUidInSelection,
        sortSelection,
    } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        emailSelection: "1:*" | string[];
        currentOffset: number;
    }

    let { emailSelection = $bindable([]), currentOffset = $bindable() }: Props =
        $props();

    let isMailboxOfCustomFolder = $derived.by(() => {
        if (SharedStore.currentAccount == "home") return false;

        return SharedStore.folders[
            SharedStore.currentAccount.email_address
        ].custom.includes(getCurrentMailbox().folder);
    });

    let groupedEmailSelection: [string, string][] = $derived.by(() => {
        if (!emailSelection) return [];

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
        const accountUidMap: Record<string, string> = {};
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
                if (!Object.hasOwn(accountUidMap, emailAddr)) {
                    accountUidMap[emailAddr] = uid;
                } else {
                    accountUidMap[emailAddr] = accountUidMap[emailAddr].concat(
                        ",",
                        uid,
                    );
                }
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

    async function markEmails(mark: string | Mark) {
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
    }

    async function unmarkEmails(mark: string | Mark) {
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

    const markAsRead = async (): Promise<void> => {
        await markEmails(Mark.Seen);
    };

    const markAsUnread = async (): Promise<void> => {
        await unmarkEmails(Mark.Seen);
    };

    const markAsImportant = async (): Promise<void> => {
        await markEmails(Mark.Flagged);
    };

    const markAsNotImportant = async (): Promise<void> => {
        await unmarkEmails(Mark.Flagged);
    };

    const copyTo = async (
        destinationFolder: string | Folder,
    ): Promise<void> => {
        // Since "moveTo/copyTo/reply/forward" options are disabled when there
        // is more than one current account(mostly "home"), groupedEmailSelection's
        // length isn't going to be more than 1, so first index is enough to cover
        // selection.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const movingEmailUids = sortSelection(groupedEmailSelection[0][1]);

        const response = await MailboxController.copyEmails(
            SharedStore.accounts.find(
                (acc) => acc.email_address === emailAddressOfSelection,
            )!,
            movingEmailUids,
            getCurrentMailbox().folder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({
                title: getErrorCopyEmailsTemplate(
                    getCurrentMailbox().folder,
                    destinationFolder,
                ),
            });
            console.error(response.message);
        }
    };

    const moveTo = async (
        destinationFolder: string | Folder,
    ): Promise<void> => {
        // Same as `copyTo()` function.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const movingEmailUids = sortSelection(groupedEmailSelection[0][1]);

        const response = await MailboxController.moveEmails(
            SharedStore.accounts.find(
                (acc) => acc.email_address === emailAddressOfSelection,
            )!,
            movingEmailUids,
            getCurrentMailbox().folder,
            destinationFolder,
            currentOffset,
        );

        if (!response.success) {
            showMessage({
                title: getErrorMoveEmailsTemplate(
                    getCurrentMailbox().folder,
                    destinationFolder,
                ),
            });
            console.error(response.message);
            return;
        }
    };

    const moveToArchive = async (): Promise<void> => {
        if (
            !(
                SharedStore.currentAccount === "home" &&
                isStandardFolder(getCurrentMailbox().folder, Folder.Inbox)
            )
        ) {
            return moveTo(Folder.Archive);
        }

        const results = await Promise.allSettled(
            groupedEmailSelection.map(async (group) => {
                const emailAddress = group[0];
                const emailUids = sortSelection(group[1]);

                const response = await MailboxController.moveEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    emailUids,
                    getCurrentMailbox().folder,
                    Folder.Archive,
                    currentOffset,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({
                title: getErrorMoveEmailsTemplate(
                    getCurrentMailbox().folder,
                    Folder.Archive,
                ),
            });
            failed.forEach((f) => console.error(f.reason));
        }
    };

    const deleteFrom = async (): Promise<void> => {
        const results = await Promise.allSettled(
            groupedEmailSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const response = await MailboxController.deleteEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    getCurrentMailbox().folder,
                    currentOffset,
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
        }
    };

    const unsubscribe = async () => {
        if (emailSelection.length > 1) return;

        // Same as `copyTo()` function.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const unsubscribingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((em) => em.uid == unsubscribingEmailUid)!;
        if (
            !Object.hasOwn(email, "list_unsubscribe") ||
            !email.list_unsubscribe
        )
            return;

        const response = await MailboxController.unsubscribe(
            SharedStore.accounts.find(
                (account) => account.email_address === emailAddressOfSelection,
            )!,
            email.list_unsubscribe!,
            email.list_unsubscribe_post,
        );

        if (!response.success) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
        }
    };

    const unsubscribe_all = async () => {
        const results = await Promise.allSettled(
            groupedEmailSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = group[1];

                const account = SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!;
                const emails = SharedStore.mailboxes[
                    emailAddress
                ].emails.current.filter(
                    (email) =>
                        isUidInSelection(uids, email.uid) &&
                        email.list_unsubscribe,
                );

                // Is at least 1 email has list_unsubscribe?
                if (emails[0].list_unsubscribe) {
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
                        throw new Error();
                    }
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
        }
    };

    const reply = async () => {
        // Same as `copyTo()` function.
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
        // Same as `copyTo()` function.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const replyingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((email) => email.uid == replyingEmailUid)!;

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
        <Context.Item onclick={markAsImportant}>
            {local.star[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Flagged)}
        <Context.Item onclick={markAsNotImportant}>
            {local.remove_star[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item onclick={markAsRead}>
            {local.mark_as_read[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item onclick={markAsUnread}>
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
            onclick={() => {
                moveTo(Folder.Inbox);
            }}
        >
            {local.move_to_inbox[DEFAULT_LANGUAGE]}
        </Context.Item>
    {:else}
        <Context.Item onclick={moveToArchive}>
            {local.move_to_archive[DEFAULT_LANGUAGE]}
        </Context.Item>
    {/if}
    <Context.Item onclick={deleteFrom}>
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
                    onclick={markAsImportant}
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
                    onclick={markAsNotImportant}
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
                    onclick={markAsRead}
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
                    onclick={markAsUnread}
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
                    onclick={() => {
                        moveTo(Folder.Inbox);
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
                    onclick={moveToArchive}
                >
                    {local.move_to_archive[DEFAULT_LANGUAGE]}
                </Button.Action>
            </div>
        {/if}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={deleteFrom}
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
                    onchange={copyTo}
                    placeholder={local.copy_to[DEFAULT_LANGUAGE]}
                >
                    {#if isMailboxOfCustomFolder}
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
                    onchange={moveTo}
                    placeholder={local.move_to[DEFAULT_LANGUAGE]}
                >
                    {#if isMailboxOfCustomFolder}
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
