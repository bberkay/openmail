<script lang="ts">
    import InboxItem from "$lib/components/Inbox/InboxItem.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Mark, type EmailWithContent } from "$lib/types";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import Select from "$lib/components/Elements/Select.svelte";
    import Option from "$lib/components/Elements/Option.svelte";

    const mailboxController = new MailboxController();
    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);
    let emailSelection: string[] = $state([]);

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

    const markEmail = async (mark: string | Mark): Promise<void> => {
        const response = await mailboxController.markEmails(emailSelection, mark);
        if(!response.success) {
            alert(response.message);
        }
    }

    const unmarkEmail = async (mark: string | Mark): Promise<void> => {
        const response = await mailboxController.unmarkEmails(emailSelection, mark);
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

    const deleteEmails = async (): Promise<void> => {
        if (confirm("Are you sure you want to delete these emails?")) {
            const response = await mailboxController.deleteEmails(emailSelection);
            if(!response.success) {
                alert(response.message);
            }
        }
    }

    const moveEmails = async (destinationFolder: string | null): Promise<void> => {
        if(!destinationFolder)
            return;

        const response = await mailboxController.moveEmails(emailSelection, destinationFolder);
        if(!response.success) {
            alert(response.message);
        }
    }

    const copyEmails = async (destinationFolder: string | null): Promise<void> => {
        if(!destinationFolder)
            return;

        const response = await mailboxController.moveEmails(emailSelection, destinationFolder);
        if(!response.success) {
            alert(response.message);
        }
    }

    function isAllSelectedEmailsAreMarked(mark: Mark): boolean {
        return emailSelection.every((uid) => {
            return SharedStore.mailboxes[0].result.emails.find(email => email.uid == uid && Object.hasOwn(email, "flags") && email.flags && email.flags.includes(mark));
        });
    }

    function isAllSelectedEmailsAreUnmarked(mark: Mark, unmark: Mark): boolean {
        return emailSelection.every((uid) => {
            return SharedStore.mailboxes[0].result.emails.find(email => email.uid == uid && Object.hasOwn(email, "flags") && email.flags && (!email.flags.includes(mark) || email.flags.includes(unmark)));
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
</script>


<h2>{SharedStore.currentFolder}</h2>
<hr />
<div style="display:flex;justify-content:space-between;align-items:center;">
    <ActionButton onclick={getPreviousEmails} class="bg-primary {currentOffset < 10 ? "disabled" : ""}">
        Previous
    </ActionButton>
    <small>
        {Math.max(1, currentOffset)} - {Math.min(totalEmailCount, currentOffset + 10)} of {totalEmailCount}
    </small>
    <ActionButton onclick={getNextEmails}  class="bg-primary {currentOffset >= totalEmailCount ? "disabled" : ""}">
        Next
    </ActionButton>
</div>
<hr />
<div style="display:flex;">
    <input type="checkbox" id="select-all" style="margin-right:10px;" onclick={selectAllShownEmails}>
    {#if emailSelection.length > 0}
        <span style="margin-right:10px;background-color:darkslategray;padding:5px;border-radius:5px;">
            {emailSelection.includes("*") ? totalEmailCount : emailSelection.length} selected.
            <button onclick={selectAllEmails}>Select all {totalEmailCount} emails</button>
        </span>
        <br>
        <ActionButton onclick={deleteEmails} class="bg-primary" style="margin-right:5px">
            Delete
        </ActionButton>
        <Select onchange={moveEmails} placeholder='Move To'>
            {#each SharedStore.customFolders[0].result as customFolder}
                <Option value={customFolder}>customFolder</Option>
            {/each}
        </Select>
        <Select onchange={copyEmails} placeholder='Copy To'>
            {#each SharedStore.customFolders[0].result as customFolder}
                <Option value={customFolder}>customFolder</Option>
            {/each}
        </Select>
        {#if isAllSelectedEmailsAreMarkedAsFlagged()}
            <ActionButton onclick={markEmailsAsNotImportant} class="bg-primary" style="margin-right:5px">
                Mark as Not Important
            </ActionButton>
        {:else if isAllSelectedEmailsAreMarkedAsNotFlagged()}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsImportant}>Mark as Important</button>
        {:else}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsNotImportant}>Mark as Not Important</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsImportant}>Mark as Important</button>
        {/if}
        {#if isAllSelectedEmailsAreMarkedAsSeen()}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsUnread}>Mark as Unread</button>
        {:else if isAllSelectedEmailsAreMarkedAsNotSeen()}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsRead}>Mark as Read</button>
        {:else}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsRead}>Mark as Read</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsUnread}>Mark as Unread</button>
        {/if}
    {:else}
        <ActionButton onclick={refreshMailbox} class="bg-primary" style="margin-right:5px" >
            Refresh
        </ActionButton>
    {/if}
</div>
<hr />
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
