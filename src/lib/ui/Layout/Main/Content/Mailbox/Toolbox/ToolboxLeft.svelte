<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { NOT_IMPLEMENTED_TEMPLATE } from "$lib/constants";
    import { type Email, Mark, Folder, type Mailbox } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import * as Context from "$lib/ui/Components/Context";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { sortSelection } from "$lib/utils";

    interface Props {
        emailSelection: "1:*" | string[];
        currentMailbox: Mailbox;
    }

    let { emailSelection = $bindable([]), currentMailbox }: Props = $props();

    let isMailboxOfCustomFolder = $derived.by(() => {
        if (SharedStore.currentAccount == "home")
            return false;

        return SharedStore.folders[
            SharedStore.currentAccount.email_address
        ].custom.includes(currentMailbox.folder);
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
        if (currentMailbox) {
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
            const targetMailbox = SharedStore.mailboxes[emailAddress].emails.current;
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
            const [emailAddress, uid] = selection.split(",")
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
        groupedEmailSelection.forEach(async (group) => {
            const emailAddress = group[0];
            const uids = sortSelection(group[1]);
            const response = await MailboxController.markEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                uids,
                mark,
                currentMailbox.folder
            );
            if (!response.success) {
                showMessage({
                    content: `Unexpected error while marking email as ${mark}`,
                });
                console.error(response.message);
            }
        });
    }

    async function unmarkEmails(mark: string | Mark) {
        groupedEmailSelection.forEach(async (group) => {
            const emailAddress = group[0];
            const uids = sortSelection(group[1]);
            const response = await MailboxController.unmarkEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                uids,
                mark,
                currentMailbox.folder
            );
            if (!response.success) {
                showMessage({
                    content: `Unexpected error while unmarking email as ${mark}`,
                });
                console.error(response.message);
            }
        });
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
            currentMailbox.folder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({ content: "Unexpected error while copying email." });
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
            currentMailbox.folder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({ content: "Unexpected error while moving email." });
            console.error(response.message);
            return;
        }
    };

    const moveToArchive = async (): Promise<void> => {
        groupedEmailSelection.forEach(async (group) => {
            const emailAddress = group[0];
            const emailUids = sortSelection(group[1]);
            const response = await MailboxController.moveEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                emailUids,
                currentMailbox.folder,
                Folder.Archive,
            );

            if (!response.success) {
                showMessage({
                    content: "Unexpected error while moving email.",
                });
                console.error(response.message);
                return;
            }
        });
    };

    const deleteFrom = async (): Promise<void> => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                groupedEmailSelection.forEach(async (group) => {
                    const emailAddress = group[0];
                    const uids = sortSelection(group[1]);
                    const response = await MailboxController.deleteEmails(
                        SharedStore.accounts.find(
                            (acc) => acc.email_address === emailAddress,
                        )!,
                        uids,
                        currentMailbox.folder,
                    );
                    if (!response.success) {
                        showMessage({
                            content: "Unexpected error while deleting email.",
                        });
                        console.error(response.message);
                    }
                });
            },
        });
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
        const accounts = SharedStore.currentAccount !== "home"
            ? [SharedStore.currentAccount]
            : SharedStore.accounts;

        let response;
        for(const account of accounts) {
            response = await MailboxController.getMailbox(account);
        }

        if (!response!.success) {
            showMessage({ content: "Error while refreshing mailboxes." });
            console.error(response!.message);
        }
    };
</script>

<Context.Root
    target=".mailbox .email"
    beforeOpen={selectEmail}
    afterClose={deselectEmail}
>
    {#if !isSelectedEmailsIncludesGivenMark(Mark.Flagged)}
        <Context.Item onclick={markAsImportant}>Star</Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Flagged)}
        <Context.Item onclick={markAsNotImportant}>Remove Star</Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item onclick={markAsRead}>Mark as Read</Context.Item>
    {/if}
    {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
        <Context.Item onclick={markAsUnread}>Mark as Unread</Context.Item>
    {/if}
    {#if emailSelection.length == 1}
        <Context.Separator />
        <Context.Item onclick={reply}>Reply</Context.Item>
        <Context.Item onclick={forward}>Forward</Context.Item>
        <Context.Separator />
        <Context.Item
            onclick={() => {
                showMessage({
                    content: NOT_IMPLEMENTED_TEMPLATE.replace(
                        "{feature}",
                        "Unsubscribe",
                    ),
                });
            }}
        >
            Unsubscribe
        </Context.Item>
    {:else if isSelectedEmailsHaveUnsubscribeOption()}
        <Context.Item
            onclick={() => {
                showMessage({
                    content: NOT_IMPLEMENTED_TEMPLATE.replace(
                        "{feature}",
                        "Unsubscribe All",
                    ),
                });
            }}
        >
            Unsubscribe All
        </Context.Item>
    {/if}
    <Context.Separator />
    <Context.Item onclick={moveToArchive}>Archive</Context.Item>
    <Context.Item onclick={deleteFrom}>Delete</Context.Item>
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
                    Star
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
                    Remove Star
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
                    Mark as Read
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
                    Mark as Unread
                </Button.Action>
            </div>
        {/if}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={moveToArchive}
            >
                Archive
            </Button.Action>
        </div>
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={deleteFrom}
            >
                Delete
            </Button.Action>
        </div>
        {#if groupedEmailSelection.length == 1}
            {@const emailAddress = groupedEmailSelection[0][0]}
            <div class="tool-separator"></div>
            <div class="tool">
                <Select.Root onchange={copyTo} placeholder="Copy To">
                    {#if isMailboxOfCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                    {#each SharedStore.folders[emailAddress].custom as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== currentMailbox.folder}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                </Select.Root>
            </div>
            <div class="tool">
                <Select.Root onchange={moveTo} placeholder="Move To">
                    {#if isMailboxOfCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                    {#each SharedStore.folders[emailAddress].custom as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== currentMailbox.folder}
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
                Refresh
            </Button.Action>
        </div>
    {/if}
</div>
