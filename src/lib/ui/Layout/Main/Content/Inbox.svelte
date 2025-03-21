<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { onMount } from "svelte";
    import { type Email, Mark, Folder } from "$lib/types";
    import { extractEmailAddress, extractFullname, startsWithAnyOf } from "$lib/utils";
    import { MAILBOX_CLEAR_SELECTION_TEMPLATE, MAILBOX_PAGINATION_TEMPLATE, MAILBOX_SELECT_ALL_TEMPLATE, MAILBOX_SELECTION_INFO_TEMPLATE } from "$lib/constants";
    import InboxItem from "$lib/ui/Layout/Main/Content/Inbox/InboxItem.svelte";
    import Icon from "$lib/ui/Components/Icon";
    import Badge from "$lib/ui/Components/Badge/Badge.svelte";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";

    type DateGroup = "Today" | "Yesterday" | "This Week" | "This Month" | "Older";
    const mailboxController = new MailboxController();

    let currentMailbox = $derived(SharedStore.mailboxes.find(
        task => task.email_address === SharedStore.currentAccount!.email_address &&
            task.result.folder === SharedStore.currentFolder
    )!.result);
    let currentMailboxUids: string[] = $derived(
        currentMailbox.emails.map((email: Email) => email.uid).flat()
    );

    let currentOffset = $state(1);
    let totalEmailCount = $derived(currentMailbox.total);
    let isAllEmailsSelected = $state(false);
    let emailSelection: string[] = $state([]);

    const customFoldersOfAccount = SharedStore.currentAccount
        ? SharedStore.customFolders.find(
            acc => acc.email_address === SharedStore.currentAccount!.email_address
        )!.result
        : [];
    const isEmailInCustomFolder = $derived(
        !startsWithAnyOf(currentMailbox.folder, Object.values(Folder))
    );

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById("select-shown") as HTMLInputElement;
    });

    function groupEmailsByDate() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const lastWeekStart = new Date(today);
        lastWeekStart.setDate(lastWeekStart.getDate() - 7);

        const lastMonthStart = new Date(today);
        lastMonthStart.setMonth(lastMonthStart.getMonth() - 1);

        const groupedEmails: Record<DateGroup, Email[]> = {
          "Today": [],
          "Yesterday": [],
          "This Week": [],
          "This Month": [],
          "Older": []
        };

        currentMailbox.emails.forEach(email => {
            const emailDate = new Date(email.date);
            emailDate.setHours(0, 0, 0, 0);

            if (emailDate.getTime() === today.getTime()) {
                groupedEmails["Today"].push(email);
            } else if (emailDate.getTime() === yesterday.getTime()) {
                groupedEmails["Yesterday"].push(email);
            } else if (emailDate >= lastWeekStart && emailDate < yesterday) {
                groupedEmails["This Week"].push(email);
            } else if (emailDate >= lastMonthStart && emailDate < lastWeekStart) {
                groupedEmails["This Month"].push(email);
            } else {
                groupedEmails["Older"].push(email);
            }
        });

        return groupedEmails;
    }

    /* Handle Selection */

    const selectShownEmails = (event: Event) => {
        /* TODO: Burada shown değil hepsi seçiliyor fakat shown
        seçilmeli, e-postalar yazdırılınca burayı da düzelt */
        emailSelection = selectShownCheckbox.checked
            ? currentMailbox.emails.map((email: Email) => email.uid).flat()
            : [];
    }

    const selectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = currentMailboxUids;
        selectAllButton.innerHTML = MAILBOX_CLEAR_SELECTION_TEMPLATE;
        selectShownCheckbox.checked = true;
        isAllEmailsSelected = true;
    }

    const deselectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = [];
        selectAllButton.innerHTML = MAILBOX_SELECT_ALL_TEMPLATE
            .replace("{total}", totalEmailCount.toString())
        selectShownCheckbox.checked = false;
        isAllEmailsSelected = false;
    }

    function isSelectedEmailsIncludesGivenMark(mark: Mark): boolean {
        if (isAllEmailsSelected) {
            return currentMailbox.emails.every(
                (email: Email) => Object.hasOwn(email, "flags") &&
                    email.flags!.includes(mark)
            );
        } else {
            return emailSelection.every((uid) => {
                return currentMailbox.emails.find(
                    (email: Email) => email.uid == uid &&
                        Object.hasOwn(email, "flags") &&
                        email.flags!.includes(mark)
                );
            });
        }
    }

    function isSelectedEmailsExcludesGivenMark(mark: Mark): boolean {
        if (isAllEmailsSelected) {
            return currentMailbox.emails.every(
                (email: Email) => Object.hasOwn(email, "flags") &&
                    !email.flags!.includes(mark)
            );
        } else {
            return emailSelection.every((uid) => {
                return currentMailbox.emails.find(
                    (email: Email) => email.uid == uid &&
                        Object.hasOwn(email, "flags") &&
                        !email.flags!.includes(mark)
                );
            });
        }
    }

    /* Email Operations */

    async function markEmails(mark: string | Mark) {
        const response = await mailboxController.markEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            showMessage({content: `Unexpected error while marking email as ${mark}`});
            console.error(response.message);
        }
    }

    async function unmarkEmails(mark: string | Mark) {
        const response = await mailboxController.unmarkEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            showMessage({content: `Unexpected error while marking email as ${mark}`});
            console.error(response.message);
        }
    }

    const markAsRead = async (): Promise<void> => {
        await markEmails(Mark.Seen);
    }

    const markAsUnread = async (): Promise<void> => {
        await unmarkEmails(Mark.Seen);
    }

    const markAsImportant = async (): Promise<void> => {
        await markEmails(Mark.Flagged);
    }

    const markAsNotImportant = async (): Promise<void> => {
        await unmarkEmails(Mark.Flagged);
    }

    const copyTo = async (destinationFolder: string | Folder): Promise<void> => {
        const response = await mailboxController.copyEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder
        );

        if(!response.success) {
            showMessage({content: "Unexpected error while copying email."});
            console.error(response.message);
        }
    }

    const moveTo = async (destinationFolder: string | Folder): Promise<void> => {
        const response = await mailboxController.moveEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder
        );

        if(!response.success) {
            showMessage({content: "Unexpected error while moving email."});
            console.error(response.message);
            return;
        }
    }

    const moveToArchive = async (): Promise<void> => {
        moveTo(Folder.Archive);
    }

    const deleteFrom = async (): Promise<void> => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                const response = await mailboxController.deleteEmails(
                    SharedStore.currentAccount,
                    emailSelection,
                    SharedStore.currentFolder
                );
                if(!response.success) {
                    showMessage({content: "Unexpected error while deleting email."});
                    console.error(response.message);
                }
            },
        })
    }

    /* Mailbox Functions */

    const refresh = async (): Promise<void> => {
        const response = await mailboxController.getMailboxes();
        if (!response.success) {
            showMessage({content: "Error while refreshing mailboxes."});
            console.error(response.message);
        }
    }

    const getPreviousEmails = async (): Promise<void> => {
        if (currentOffset <= 10)
            return;

        const offset_start = Math.max(1, currentOffset - 10);
        const offset_end = Math.max(1, currentOffset);
        const response = await mailboxController.paginateEmails(
            SharedStore.currentAccount,
            offset_start,
            offset_end
        );
        if (response.success) {
            currentOffset = Math.max(1, offset_start);
        } else {
            showMessage({content: "Error while getting previous emails."});
            console.error(response.message)
        }
    }

    const getNextEmails = async (): Promise<void> => {
        if (currentOffset >= totalEmailCount)
            return;

        const offset_start = Math.min(totalEmailCount, currentOffset + 10);
        const offset_end = Math.min(totalEmailCount, currentOffset + 10 + 10);
        const response = await mailboxController.paginateEmails(
            SharedStore.currentAccount,
            offset_start,
            offset_end
        );
        if (response.success) {
            currentOffset = Math.max(1, offset_start);
        } else {
            showMessage({content: "Error while getting next emails."});
            console.error(response.message)
        }
    }
</script>

<div class="toolbox">
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
            <div class="tool-separator"></div>
            <div class="tool">
                {#if customFoldersOfAccount}
                    <Select.Root onchange={copyTo} placeholder='Copy To'>
                        {#each customFoldersOfAccount as customFolder}
                            {#if customFolder !== currentMailbox.folder}
                                <Select.Option value={customFolder}>{customFolder}</Select.Option>
                            {/if}
                        {/each}
                        {#if isEmailInCustomFolder}
                            <!-- Add inbox option if email is in custom folder -->
                            <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                        {/if}
                    </Select.Root>
                {/if}
            </div>
            <div class="tool">
                {#if customFoldersOfAccount}
                    <Select.Root onchange={moveTo} placeholder='Move To'>
                        {#each customFoldersOfAccount as customFolder}
                            {#if customFolder !== currentMailbox.folder}
                                <Select.Option value={customFolder}>{customFolder}</Select.Option>
                                {/if}
                            {/each}
                        {#if isEmailInCustomFolder}
                            <!-- Add inbox option if email is in custom folder -->
                            <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                            {/if}
                    </Select.Root>
                {/if}
            </div>
        {:else}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={refresh}
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
                                isAllEmailsSelected
                                    ? totalEmailCount
                                    : emailSelection.length
                            ).toString()
                        )
                }
            </span>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={isAllEmailsSelected ? deselectAllEmails : selectAllEmails}
            >
                {
                    MAILBOX_SELECT_ALL_TEMPLATE
                        .replace("{total}", totalEmailCount.toString())
                }
            </Button.Basic>
        </div>
    {/if}

    {#each Object.entries(groupEmailsByDate()) as group}
        <div class="group-separator">
            <div class="timeline-label">
                <span>{group[0]}</span>
            </div>
        </div>
        <div class="email-group">
            {#each group[1] as email}
                <div class="email">
                    <div class="email-sender">
                        <input type="checkbox" class="select-email-checkbox" bind:group={emailSelection} value={email.uid}>
                        <span>{extractFullname(email.sender) || extractEmailAddress(email.sender)}</span>
                        <div class="new-message-icon">
                            <span>New</span>
                        </div>
                    </div>
                    <div class="email-message">
                        {#if Object.hasOwn(email, "attachments") && email.attachments!.length > 0}
                            <div class="message-attachment-icon">
                                <Icon name="attachment" />
                            </div>
                        {/if}
                        <div class="message-subject">
                            <span>{email.subject}</span>
                        </div>
                        <span class="message-separator">---</span>
                        <div class="message-body">
                            <span>{email.body}</span>
                        </div>
                        <div class="message-flags tags">
                            {#if Object.hasOwn(email, "flags") && email.flags!.length > 0}
                                {#each email.flags! as flag}
                                    <Badge content={flag} />
                                {/each}
                            {/if}
                        </div>
                    </div>
                    <div class="email-date">
                        <span>{email.date}</span>
                    </div>
                </div>
            {/each}
        </div>
    {/each}
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
