<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, GetRoutes, PostRoutes } from "$lib/services/ApiService";
    import { Folder, Mark, type EmailSummary } from "$lib/types";

    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);
    let folderSelection = $state("Move to");
    let emailSelection: string[] = $state([]);

    async function makeAnApiRequest(event: Event, callback: () => Promise<void>) {
        folderSelection = "Move to";
        emailSelection = [];
        const eventButton = event.target as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton })

        await callback();

        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
    }

    async function refreshMailboxes(event: Event) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.get(
                SharedStore.server,
                GetRoutes.GET_MAILBOXES,
                {
                    pathParams: {
                        accounts: SharedStore.accounts
                            .map((account) => account.email_address)
                            .join(",")
                    }
                }
            );

            if (response.success && response.data) {
                SharedStore.mailboxes = response.data;
                SharedStore.selectedFolder = response.data[0].result.folder;
            }
        })
    }

    async function paginateEmails(event: Event, offset_start: number, offset_end: number) {
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
                currentOffset = Math.min(0, offset_start);
                SharedStore.mailboxes = response.data;
            }
        })
    }

    async function getPreviousEmails(event: Event) {
        if (currentOffset <= 10)
            return;

        paginateEmails(
            event,
            Math.max(0, currentOffset - 10),
            Math.max(0, currentOffset)
        );
    }

    async function getNextEmails(event: Event) {
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

    async function markEmail(event: Event, mark: string | Mark, folder: string | Folder = Folder.Inbox) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MARK_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    mark: mark,
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection[emailSelection.length - 1] + ":" + emailSelection[0],
                    folder: folder
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
            }
        })
    }

    async function unmarkEmail(event: Event, mark: string | Mark, folder: string | Folder = Folder.Inbox) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.UNMARK_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    mark: mark,
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection[emailSelection.length - 1] + ":" + emailSelection[0],
                    folder: folder
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
            }
        })
    }

    async function markEmailsAsRead(event: Event) {
        markEmail(event, Mark.Seen, Folder.Inbox);
    }

    async function markEmailsAsUnread(event: Event) {
        unmarkEmail(event, Mark.Seen, Folder.Inbox);
    }

    async function markEmailsAsImportant(event: Event) {
        markEmail(event, Mark.Flagged, Folder.Inbox);
    }

    async function markEmailsAsNotImportant(event: Event) {
        unmarkEmail(event, Mark.Flagged, Folder.Inbox);
    }

    async function deleteEmails(event: Event) {
        makeAnApiRequest(event, async () => {
            confirm("Are you sure you want to delete these emails?");

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.DELETE_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection[emailSelection.length - 1] + ":" + emailSelection[0],
                    folder: Folder.Inbox
                }
            );

            if (response.success) {
                SharedStore.mailboxes[0].result.emails = SharedStore.mailboxes[0].result.emails.filter((email: EmailSummary) => !emailSelection.includes(email.uid));
            }
        })
    }

    async function moveEmail(event: Event) {
        makeAnApiRequest(event, async () => {
            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MOVE_EMAIL,
                {
                    account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection[emailSelection.length - 1] + ":" + emailSelection[0],
                    source_folder: Folder.Inbox,
                    destination_folder: folderSelection
                }
            );

            if (response.success) {
                paginateEmails(event, currentOffset, currentOffset + 10);
            }
        })
    }
</script>

<div class="card" style="flex-grow:1;">
    <h2>{SharedStore.selectedFolder}</h2>
    <hr />
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <button class = "bg-primary" onclick={getPreviousEmails} disabled={currentOffset <= 10}>Previous</button>
        <small>
            {Math.max(1, currentOffset)} - {Math.min(totalEmailCount, currentOffset + 10)} of {totalEmailCount}
        </small>
        <button class = "bg-primary" onclick={getNextEmails} disabled={currentOffset >= totalEmailCount}>Next</button>
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
            <select class = "bg-primary" style="margin-right:5px;width:80px;" bind:value={folderSelection} onchange={moveEmail}>
                <option disabled selected>Move to</option>
                {#each SharedStore.folders[0].result as folder}
                    <option value="{folder}">{folder}</option>
                {/each}
            </select>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsImportant}>Mark as Important</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsNotImportant}>Mark as Not Important</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsRead}>Mark as Read</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsUnread}>Mark as Unread</button>
        {:else}
            <button class = "bg-primary" style="margin-right:5px;" onclick={refreshMailboxes}>Refresh</button>
        {/if}
    </div>
    <hr />
    <div>
        {#each SharedStore.mailboxes as account}
            {#each account.result.emails as email}
                <div style="display:flex;">
                    <input type="checkbox" style="margin-right:10px;" bind:group={emailSelection} value={email.uid}>
                    <div style="flex-grow:1">
                        <InboxItem owner={account.email_address} email={email} />
                    </div>
                </div>
            {/each}
        {/each}
    </div>
</div>
