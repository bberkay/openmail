<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { NOT_IMPLEMENTED_TEMPLATE } from "$lib/constants";
    import { type Email, Mark, Folder } from "$lib/types";
    import { startsWithAnyOf } from "$lib/utils";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import * as Context from "$lib/ui/Components/Context";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";

    interface Props {
        emailSelection: "1:*" | string[];
    }

    let { emailSelection = $bindable([]) }: Props = $props();

    // When the `emailSelection` will be something like this:
    // ["account1@mail.com,123", "account1@mail.com,124", "account2@mail.com,123"]
    // the `groupedEmailSelection` will be something like this:
    // [["account1@mail.com", "123,124"], ["account2@mail.com", "123"]]
    // and with this way, we are minimizing api calls from this:
    // C: A101 +STORE FLAG account1@mail.com 123
    // C: A102 +STORE FLAG account1@mail.com 124
    // C: A103 +STORE FLAG account1@mail.com 125
    // to this:
    // C: A101 +STORE FLAG account1@mail.com 123, 124
    // C: A102 +STORE FLAG account1@mail.com 125
    let groupedEmailSelection: [string, string][] = $state([]);

    let isMailboxOfCustomFolder = $derived.by(() => {
        if (SharedStore.currentAccount == "home")
            return false;
        return !startsWithAnyOf(
            SharedStore.currentMailbox.folder,
            Object.values(Folder),
        );
    });

    let selectShownCheckbox: HTMLInputElement;
    let shownEmailUids: string[] = $state([]);
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    function groupEmailSelectionByAccount() {
        const accountUidMap: Record<string, string> = {};
        if (emailSelection === "1:*") {
            SharedStore.accounts.forEach((account) => {
                if (["home", account].includes(SharedStore.currentAccount)) {
                    accountUidMap[account.email_address] = "1:*";
                }
            });
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
        return accountUidMap;
    }

    $effect(() => {
        if (SharedStore.currentMailbox) {
            document
                .querySelectorAll<HTMLInputElement>(
                    ".mailbox .email-selection-checkbox",
                )
                .forEach((element) => {
                    shownEmailUids.push(element.value);
                });
        }

        if (emailSelection) {
            groupedEmailSelection = Object.entries(
                groupEmailSelectionByAccount(),
            );
        }
    });

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

    function isSelectedEmailsIncludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((uid) => {
            return SharedStore.currentMailbox.emails.current.find(
                (email: Email) =>
                    email.uid == uid &&
                    Object.hasOwn(email, "flags") &&
                    email.flags!.includes(mark),
            );
        });
    }

    function isSelectedEmailsExcludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((uid) => {
            return SharedStore.currentMailbox.emails.current.find(
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
            const uids = group[1];
            const response = await MailboxController.markEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                uids,
                mark,
                SharedStore.currentFolder,
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
            const uids = group[1];
            const response = await MailboxController.unmarkEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                uids,
                mark,
                SharedStore.currentFolder,
            );
            if (!response.success) {
                showMessage({
                    content: `Unexpected error while marking email as ${mark}`,
                });
                console.error(response.message);
            }
        });
    }

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
        // Since "move to" option is disabled when there is more than one
        // current account(mostly "home"), groupedEmailSelection's length
        // isn't going to be more than 1 so first index is enough to
        // cover up selection.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const movingEmailUids = groupedEmailSelection[0][1];

        const response = await MailboxController.copyEmails(
            SharedStore.currentAccount !== "home"
                ? SharedStore.currentAccount
                : SharedStore.accounts.find(
                      (acc) =>
                          acc.email_address === emailAddressOfSelection,
                  )!,
            movingEmailUids,
            SharedStore.currentFolder,
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
        // Since "move to" option is disabled when there is more than one
        // current account(mostly "home"), groupedEmailSelection's length
        // isn't going to be more than 1 so first index is enough to
        // cover up selection.
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const movingEmailUids = groupedEmailSelection[0][1];

        const response = await MailboxController.moveEmails(
            SharedStore.currentAccount !== "home"
                ? SharedStore.currentAccount
                : SharedStore.accounts.find(
                      (acc) =>
                          acc.email_address === emailAddressOfSelection,
                  )!,
            movingEmailUids,
            SharedStore.currentFolder,
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
            const emailUids = group[1];
            const response = await MailboxController.moveEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!,
                emailUids,
                SharedStore.currentFolder,
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
                    const uids = group[1];
                    const response = await MailboxController.deleteEmails(
                        SharedStore.accounts.find(
                            (acc) => acc.email_address === emailAddress,
                        )!,
                        uids,
                        SharedStore.currentFolder,
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

    function isSelectedEmailsHaveUnsubscribeOption() {
        return groupedEmailSelection.every((group) => {
            const emailAddress = group[0];
            const uids = group[1].split(",");
            const emails = SharedStore.mailboxes[emailAddress].emails.current;
            return uids
                .every((uid) =>
                    emails.find(
                        (email) => email.uid == uid && !!email.list_unsubscribe,
                    ),
                );
        });
    }

    const reply = async () => {
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const replyingEmailUid = groupedEmailSelection[0][1];
        const email = SharedStore.mailboxes[emailAddressOfSelection].emails.current.find(email => email.uid == replyingEmailUid)!;
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
        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const replyingEmailUid = groupedEmailSelection[0][1]
        const email = SharedStore.mailboxes[emailAddressOfSelection].emails.current.find(email => email.uid == replyingEmailUid)!;
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
        const response = await MailboxController.getMailboxes(
            SharedStore.currentAccount === "home"
                ? SharedStore.accounts
                : SharedStore.currentAccount,
        );
        if (!response.success) {
            showMessage({ content: "Error while refreshing mailboxes." });
            console.error(response.message);
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
        {#if groupedEmailSelection.length < 2}
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
                    {#each SharedStore.customFolders[emailAddress] as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== SharedStore.currentMailbox.folder}
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
                    {#each SharedStore.customFolders[emailAddress] as customFolder}
                        {#if SharedStore.currentAccount === "home" || customFolder !== SharedStore.currentMailbox.folder}
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
