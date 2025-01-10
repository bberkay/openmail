<script lang="ts">
    import { mount, onMount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, GetRoutes, PostRoutes } from "$lib/services/ApiService";
    import { Folder, Mark, type EmailSummary, type EmailWithContent } from "$lib/types";

    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);
    let moveFolderSelection = $state("Move to");
    let copyFolderSelection = $state("Copy to");
    let emailSelection: string[] = $state([]);

    interface Props {
        showContent: (email: EmailWithContent) => void;
    }

    let { showContent }: Props = $props();

    async function makeAnApiRequest(event: Event, callback: () => Promise<void>) {
        const eventButton = event.target as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton })

        await callback();

        emailSelection = [];
        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
    }

    function refreshMailbox(event: Event) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.get(
                SharedStore.server,
                GetRoutes.GET_MAILBOXES,
                {
                    pathParams: {
                        accounts: SharedStore.accounts[0].email_address
                    },
                    queryParams: {
                        folder: SharedStore.currentFolder
                    }
                }
            );

            if (response.success && response.data) {
                SharedStore.mailboxes = response.data;
            } else {
                alert(response.message);
            }
        })
    }

    function paginateEmails(event: Event, offset_start: number, offset_end: number) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.get(
                SharedStore.server,
                GetRoutes.PAGINATE_MAILBOXES,
                {
                    pathParams: {
                        accounts: SharedStore.accounts.map((account) => account.email_address).join(", "),
                        offset_start: offset_start,
                        offset_end: offset_end,
                    }
                }
            );

            if (response.success && response.data) {
                currentOffset = Math.max(0, offset_start);
                SharedStore.mailboxes = response.data;
            } else {
                alert(response.message);
            }
        })
    }

    function getPreviousEmails(event: Event) {
        if (currentOffset <= 10)
            return;

        paginateEmails(
            event,
            Math.max(0, currentOffset - 10),
            Math.max(0, currentOffset)
        );
    }

    function getNextEmails(event: Event) {
        if (currentOffset >= totalEmailCount)
            return;

        paginateEmails(
            event,
            Math.min(totalEmailCount, currentOffset + 10),
            Math.min(totalEmailCount, currentOffset + 10 + 10)
        )
    }

    function selectAllShownEmails(event: Event) {
        const selectAllCheckbox = event.target as HTMLInputElement;
        emailSelection = selectAllCheckbox.checked
            ? SharedStore.mailboxes.map((account) => account.result.emails.map((email) => email.uid)).flat()
            : [];
    }

    function selectAllEmails(event: Event) {
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

    function markEmail(event: Event, mark: string | Mark) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MARK_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    mark: mark,
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection.join(","),
                    folder: SharedStore.currentFolder
                }
            );

            if (response.success) {
                emailSelection.forEach((uid: string) => {
                    SharedStore.mailboxes[0].result.emails.forEach((email: EmailSummary) => {
                        if (email.uid === uid && Object.hasOwn(email, "flags") && email.flags) {
                            email.flags.push(mark);
                        }
                    })
                })
            } else {
                alert(response.message);
            }
        })
    }

    function unmarkEmail(event: Event, mark: string | Mark) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.UNMARK_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    mark: mark,
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection.join(","),
                    folder: SharedStore.currentFolder
                }
            );

            if (response.success) {
                emailSelection.forEach((uid: string) => {
                    SharedStore.mailboxes[0].result.emails.forEach((email: EmailSummary) => {
                        if (email.uid === uid && Object.hasOwn(email, "flags") && email.flags) {
                            email.flags = email.flags.filter((flag: string) => flag !== mark);
                        }
                    })
                })
            } else {
                alert(response.message);
            }
        })
    }

    function markEmailsAsRead(event: Event) {
        markEmail(event, Mark.Seen);
    }

    function markEmailsAsUnread(event: Event) {
        unmarkEmail(event, Mark.Seen);
    }

    function markEmailsAsImportant(event: Event) {
        markEmail(event, Mark.Flagged);
    }

    function markEmailsAsNotImportant(event: Event) {
        unmarkEmail(event, Mark.Flagged);
    }

    function deleteEmails(event: Event) {
        makeAnApiRequest(event, async () => {
            confirm("Are you sure you want to delete these emails?");

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.DELETE_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection.join(","),
                    folder: SharedStore.currentFolder
                }
            );

            if (response.success) {
                refreshMailbox(event);
            } else {
                alert(response.message);
            }
        })
    }

    function moveEmail(event: Event) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MOVE_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection.join(","),
                    source_folder: SharedStore.currentFolder,
                    destination_folder: moveFolderSelection
                }
            );

            if (response.success) {
                refreshMailbox(event);
            } else {
                alert(response.message);
            }

            moveFolderSelection = "Move to";
        })
    }

    function copyEmail(event: Event) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MOVE_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection.join(","),
                    source_folder: SharedStore.currentFolder,
                    destination_folder: copyFolderSelection
                }
            );

            if (!response.success) {
                alert(response.message);
            }

            copyFolderSelection = "Copy to";
        })
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
    {#if currentOffset < 10}
        <button class = "bg-primary" disabled>Previous</button>
    {:else}
        <button class = "bg-primary" onclick={getPreviousEmails}>Previous</button>
    {/if}

    <small>
        {Math.max(1, currentOffset)} - {Math.min(totalEmailCount, currentOffset + 10)} of {totalEmailCount}
    </small>

    {#if currentOffset >= totalEmailCount}
        <button class = "bg-primary" disabled>Next</button>
    {:else}
        <button class = "bg-primary" onclick={getNextEmails}>Next</button>
    {/if}
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
        <button class = "bg-primary" style="margin-right:5px;" onclick={deleteEmails}>Delete</button>
        <select class = "bg-primary" style="margin-right:5px;width:80px;" bind:value={moveFolderSelection} onchange={moveEmail}>
            <option disabled selected>Move to</option>
            {#each SharedStore.customFolders[0].result as folder}
                <option value="{folder}">{folder}</option>
            {/each}
        </select>
        <select class = "bg-primary" style="margin-right:5px;width:80px;" bind:value={copyFolderSelection} onchange={copyEmail}>
            <option disabled selected>Copy to</option>
            {#each SharedStore.customFolders[0].result as folder}
                <option value="{folder}">{folder}</option>
            {/each}
        </select>
        {#if isAllSelectedEmailsAreMarkedAsFlagged()}
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsNotImportant}>Mark as Not Important</button>
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
        <button class = "bg-primary" style="margin-right:5px;" onclick={refreshMailbox}>Refresh</button>
    {/if}
</div>
<hr />
<div>
    {#each SharedStore.mailboxes as account}
        {#each account.result.emails as email}
            <div style="display:flex;">
                <input type="checkbox" style="margin-right:10px;" bind:group={emailSelection} value={email.uid}>
                <div style="flex-grow:1">
                    <InboxItem owner={account.email_address} {email} {showContent}  />
                </div>
            </div>
        {/each}
    {/each}
</div>
