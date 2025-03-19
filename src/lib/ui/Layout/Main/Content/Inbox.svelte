<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email, Mark, type Mailbox, Folder } from "$lib/types";
    import InboxItem from "$lib/ui/Layout/Main/Content/Inbox/InboxItem.svelte";
    import * as Select from "$lib/ui/Elements/Select";
    import * as Input from "$lib/ui/Elements/Input";
    import * as Button from "$lib/ui/Elements/Button";
    import { MAILBOX_PAGINATION_TEMPLATE, MAILBOX_SELECTION_ALL_TEMPLATE, MAILBOX_SELECTION_INFO_TEMPLATE } from "$lib/constants";

    /* Constants */

    const mailboxController = new MailboxController();

    /* Variables */

    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);
    let emailSelection: string[] = $state([]);

    /* Inbox Functions */

    const refreshMailbox = async (): Promise<void> => {
        const response = await mailboxController.getMailboxes();
        if (!response.success) {
            alert(response.message);
        }
    }

    const getPreviousEmails = async () => {
        if (currentOffset <= 10)
            return;

        const offset_start = Math.max(0, currentOffset - 10);
        const offset_end = Math.max(0, currentOffset);
        const response = await mailboxController.paginateEmails(offset_start, offset_end);
        if (response.success) {
            currentOffset = Math.max(0, offset_start);
        } else {
            alert(response.message);
        }
    }

    const getNextEmails = async () => {
        if (currentOffset >= totalEmailCount)
            return;

        const offset_start = Math.min(totalEmailCount, currentOffset + 10);
        const offset_end = Math.min(totalEmailCount, currentOffset + 10 + 10);
        const response = await mailboxController.paginateEmails(offset_start, offset_end);
        if (response.success) {
            currentOffset = Math.max(0, offset_start);
        } else {
            alert(response.message);
        }
    }

    /* Selection Functions */

    const selectAllShownEmails = (event: Event) => {
        const selectAllCheckbox = event.target as HTMLInputElement;
        emailSelection = selectAllCheckbox.checked
            ? SharedStore.mailboxes.map((account) => account.result.emails.map((email) => email.uid)).flat()
            : [];
    }

    const selectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        const selectAllCheckbox = document.getElementById("select-all") as HTMLInputElement;
        if (emailSelection.includes("*")) {
            emailSelection = [];
            selectAllButton.innerText = "Select all";
            selectAllCheckbox.checked = false;
        } else {
            emailSelection.push("*");
            selectAllButton.innerText = "Clear selection";
        }
    }

    function isAllSelectedEmailsAreMarked(mark: Mark): boolean {
        return emailSelection.every((uid) => {
            return SharedStore.mailboxes[0].result.emails.find((email: Email) => email.uid == uid && Object.hasOwn(email, "flags") && email.flags && email.flags.includes(mark));
        });
    }

    function isAllSelectedEmailsAreUnmarked(mark: Mark, unmark: Mark): boolean {
        return emailSelection.every((uid) => {
            return SharedStore.mailboxes[0].result.emails.find((email: Email) => email.uid == uid && Object.hasOwn(email, "flags") && email.flags && (!email.flags.includes(mark) || email.flags.includes(unmark)));
        });
    }

    function isAllSelectedEmailsAreMarkedAsFlagged(): boolean {
        return isAllSelectedEmailsAreMarked(Mark.Flagged);
    }

    function isAllSelectedEmailsAreMarkedAsSeen(): boolean {
        return isAllSelectedEmailsAreMarked(Mark.Seen);
    }

    function isAllSelectedEmailsAreMarkedAsNotFlagged(): boolean {
        return isAllSelectedEmailsAreUnmarked(Mark.Flagged, Mark.Unflagged);
    }

    function isAllSelectedEmailsAreMarkedAsNotSeen(): boolean {
        return isAllSelectedEmailsAreUnmarked(Mark.Seen, Mark.Unseen);
    }

    /* Email Operations */

    const deleteEmails = async (): Promise<void> => {
        if (!SharedStore.currentAccount || !SharedStore.currentFolder) {
            alert("Current account and folder should be selected");
            return;
        }

        if (confirm("Are you sure you want to delete these emails?")) {
            const response = await mailboxController.deleteEmails(
                SharedStore.currentAccount,
                emailSelection,
                SharedStore.currentFolder
            );
            if(!response.success) {
                alert(response.message);
            }
        }
    }

    const moveEmails = async (destinationFolder: string | null): Promise<void> => {
        if (!SharedStore.currentAccount || !SharedStore.currentFolder) {
            alert("Current account and folder should be selected");
            return;
        }

        if(!destinationFolder) {
            alert("Destination folder is not selected");
            return;
        }

        const response = await mailboxController.moveEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder
        );
        if(!response.success) {
            alert(response.message);
        }
    }

    const copyEmails = async (destinationFolder: string | null): Promise<void> => {
        if (!SharedStore.currentAccount || !SharedStore.currentFolder) {
            alert("Current account and folder should be selected");
            return;
        }

        if(!destinationFolder) {
            alert("Destination folder is not selected");
            return;
        }

        const response = await mailboxController.moveEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder
        );
        if(!response.success) {
            alert(response.message);
        }
    }

    const markEmail = async (mark: string | Mark): Promise<void> => {
        if (!SharedStore.currentAccount || !SharedStore.currentFolder) {
            alert("Current account and folder should be selected");
            return;
        }

        const response = await mailboxController.markEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            alert(response.message);
        }
    }

    const unmarkEmail = async (mark: string | Mark): Promise<void> => {
        if (!SharedStore.currentAccount || !SharedStore.currentFolder) {
            alert("Current account and folder should be selected");
            return;
        }

        const response = await mailboxController.unmarkEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            alert(response.message);
        }
    }

    const markEmailsAsRead = async (): Promise<void> => {
        await markEmail(Mark.Seen);
    }

    const markEmailsAsUnread = async (): Promise<void> => {
        await unmarkEmail(Mark.Seen);
    }

    const markEmailsAsImportant = async (): Promise<void> => {
        markEmail(Mark.Flagged);
    }

    const markEmailsAsNotImportant = async (): Promise<void> => {
        unmarkEmail(Mark.Flagged);
    }
</script>

<div class="toolbox">
    <div class="toolbox-left">
        <div class="tool">
            <Input.Basic
                type="checkbox"
                onclick={selectAllShownEmails}
            />
        </div>
        {#if emailSelection.length > 0}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={deleteEmails}
                >
                    Delete
                </Button.Action>
            </div>
            <div class="tool">
                <Select.Root onchange={moveEmails} placeholder='Move To'>
                    {#each SharedStore.customFolders[0].result as customFolder}
                        <Select.Option value={customFolder}>{customFolder}</Select.Option>
                    {/each}
                     {#if SharedStore.currentFolder && !SharedStore.standardFolders[0].result.includes(SharedStore.currentFolder)}
                        <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                    {/if}
                </Select.Root>
            </div>
            <div class="tool">
                <Select.Root onchange={copyEmails} placeholder='Copy To'>
                    {#each SharedStore.customFolders[0].result as customFolder}
                        <Select.Option value={customFolder}>{customFolder}</Select.Option>
                    {/each}
                    {#if SharedStore.currentFolder && !SharedStore.standardFolders[0].result.includes(SharedStore.currentFolder)}
                        <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                    {/if}
                </Select.Root>
            </div>
            {#if !isAllSelectedEmailsAreMarkedAsNotFlagged()}
                <div class="tool">
                    <Button.Action
                        type="button"
                        class="btn-inline"
                        onclick={markEmailsAsNotImportant}
                    >
                        Mark as Not Important
                    </Button.Action>
                </div>
            {/if}
            {#if !isAllSelectedEmailsAreMarkedAsFlagged()}
                <div class="tool">
                    <Button.Action
                        type="button"
                        class="btn-inline"
                        onclick={markEmailsAsImportant}
                    >
                        Mark as Important
                    </Button.Action>
                </div>
            {/if}
            {#if !isAllSelectedEmailsAreMarkedAsSeen()}
                <div class="tool">
                    <Button.Action
                        type="button"
                        class="btn-inline"
                        onclick={markEmailsAsRead}
                    >
                        Mark as Read
                    </Button.Action>
                </div>
            {/if}
            {#if !isAllSelectedEmailsAreMarkedAsNotSeen()}
                <div class="tool">
                    <Button.Action
                        type="button"
                        class="btn-inline"
                        onclick={markEmailsAsUnread}
                    >
                        Mark as Unread
                    </Button.Action>
                </div>
            {/if}
        {:else}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={refreshMailbox}
                >
                    Refresh
                </Button.Action>
            </div>
        {/if}
    </div>
    <div class="toolbox-right">
        <div class="pagination">
            <Button.Action
                type="button"
                class="btn-inline {currentOffset < 10 ? "disabled" : ""}"
                onclick={getPreviousEmails}
            >
                Prev
            </Button.Action>
            <small>
                {
                    MAILBOX_PAGINATION_TEMPLATE
                        .replace("{offset_start}", Math.max(1, currentOffset).toString())
                        .replace("{offset_end}", Math.min(totalEmailCount, currentOffset + 10).toString())
                        .replace("{total}", totalEmailCount.toString())
                        .trim()
                }
            </small>
            <Button.Action
                type="button"
                class="btn-inline {currentOffset >= totalEmailCount ? "disabled" : ""}"
                onclick={getNextEmails}
            >
                Next
            </Button.Action>
        </div>
    </div>
</div>

<div class="mailbox">
    {#if emailSelection.length > 0}
        <div class="selection-info">
            <span>
                {
                    MAILBOX_SELECTION_INFO_TEMPLATE
                        .replace(
                            "{selection_count}",
                            (
                                emailSelection.includes("*")
                                    ? totalEmailCount
                                    : emailSelection.length
                            ).toString()
                        )
                }
            </span>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={selectAllEmails}
            >
                {
                    MAILBOX_SELECTION_ALL_TEMPLATE
                        .replace("{total}", totalEmailCount.toString())
                }
            </Button.Basic>
        </div>
    {/if}
    <div class="group-separator">
        <div class="timeline-label">
            <span>Today</span>
        </div>
    </div>
    <div class="email-group">
        <div class="email">
            <div class="email-sender">
                <input type="checkbox" class="select-email-checkbox">
                <span>Emily Davis</span>
                <div class="new-message-icon">
                    <span>New</span>
                </div>
            </div>
            <div class="email-message">
                <div class="message-attachment-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
                        <path d="M209.66,122.34a8,8,0,0,1,0,11.32l-82.05,82a56,56,0,0,1-79.2-79.21L147.67,35.73a40,40,0,1,1,56.61,56.55L105,193A24,24,0,1,1,71,159L154.3,74.38A8,8,0,1,1,165.7,85.6L82.39,170.31a8,8,0,1,0,11.27,11.36L192.93,81A24,24,0,1,0,159,47L59.76,147.68a40,40,0,1,0,56.53,56.62l82.06-82A8,8,0,0,1,209.66,122.34Z"></path>
                    </svg>
                </div>
                <div class="message-subject">
                    <span>Meeting Tomorrow</span>
                </div>
                <span class="message-separator">---</span>
                <div class="message-body">
                    <span>Hi, let's have a meet reviewing the project details and have
                    some ideas I'd like to share...</span>
                </div>
                <div class="message-flags tags">
                    <span class="badge">Important</span>
                </div>
            </div>
            <div class="email-date">
                <span>12 Jun 1902</span>
            </div>
        </div>
    </div>
</div>

<div>
    {#each SharedStore.mailboxes as account}
        {#each account.result.emails as email}
            <div style="display:flex;">
                <input type="checkbox" style="margin-right:10px;" bind:group={emailSelection} value={email.uid}>
                <div style="flex-grow:1">
                    <InboxItem account={account} folder={account.result.folder} email={email} />
                </div>
            </div>
        {/each}
    {/each}
</div>

<style>
    :global {
        .mailbox {
            display: flex;
            flex-direction: column;
            width: 100%;
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);

            & .selection-info {
                width: 100%;
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                padding: var(--spacing-sm);
                padding-bottom: calc(var(--spacing-sm) / 1.3);
                text-align: center;
                background-color: var(--color-border-subtle);
                border-bottom: 1px solid var(--color-border);
            }

            & .group-separator {
                width: 100%;
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                padding: var(--spacing-sm);
                padding-bottom: calc(var(--spacing-sm) / 1.3);
                text-align: center;
                border-bottom: 1px solid var(--color-border-subtle);

                & .timeline-label {
                    font-weight: var(--font-weight-bold);
                    text-transform: uppercase;
                }
            }

            & .email-group {
                display: flex;
                flex-direction: column;

                &:last-child {
                    & .email:last-child{
                        border-bottom: none;
                    }
                }

                & .email {
                    display: flex;
                    flex-direction: row;
                    justify-content: space-between;
                    padding: var(--spacing-sm);
                    border-bottom: 1px solid var(--color-border-subtle);
                    cursor: pointer;

                    &:hover {
                        background-color: var(--color-hover);
                    }

                    & .email-sender {
                        display: flex;
                        align-items: center;
                        gap: var(--spacing-xs);
                        width: 20%;

                        & .select-email-checkbox {
                            margin-right: var(--spacing-2xs);
                        }

                        & .new-message-icon {
                            font-size: var(--font-size-xs);
                            padding: 0px var(--spacing-xs);
                            color: var(--color-white);
                            background-color: var(--color-info);
                            border-radius: var(--radius-sm);
                            font-weight: var(--font-weight-bold);
                        }
                    }

                    & .email-message {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        gap: var(--spacing-xs);

                        & .message-separator {
                            color: var(--color-text-secondary);
                        }

                        & .message-body {
                            color: var(--color-text-secondary);
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        }

                        & .message-flags {
                            font-size: var(--font-size-xs);
                        }

                        & .message-attachment-icon {
                            margin-left: calc(-1 * var(--spacing-lg));
                        }
                    }

                    & .email-date {
                        color: var(--color-text-secondary);
                    }
                }
            }
        }
    }
</style>
