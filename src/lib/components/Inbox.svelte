<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, GetRoutes, PostRoutes } from "$lib/services/ApiService";
    import type { EmailSummary } from "$lib/types";

    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);
    let emailSelection: string[] = $state([]);

    async function paginateEmails(event: Event, offset_start: number, offset_end: number) {
        const paginateButton = event.target as HTMLButtonElement;
        paginateButton.disabled = true;
        const temp = paginateButton.innerText;
        paginateButton.innerText = '';
        const loader = mount(Loader, {
            target: paginateButton
        });

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

        paginateButton.disabled = false;
        unmount(loader);
        paginateButton.innerText = temp;
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

    async function markEmailsAsRead(event: Event) {
        const markAsReadButton = event.target as HTMLButtonElement;
        markAsReadButton.disabled = true;
        const temp = markAsReadButton.innerText;
        markAsReadButton.innerText = "";
        const loader = mount(Loader, {
            target: markAsReadButton
        })

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MARK_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                mark: "\\Seen",
                sequence_set: emailSelection.includes("*") ? "1:*" : emailSelection[emailSelection.length - 1] + ":" + emailSelection[0],
                folder: "INBOX"
            }
        );

        if (response.success) {
            emailSelection.forEach((uid: string) => {
                SharedStore.mailboxes[0].result.emails.forEach((email: EmailSummary) => {
                    if (email.uid === uid && Object.hasOwn(email, "flags") && email.flags) {
                        email.flags.push("Seen");
                    }
                })
            })
        }

        markAsReadButton.disabled = false;
        markAsReadButton.innerText = temp;
        unmount(loader);
    }

    async function refreshMailboxes(event: Event) {
        const refreshButton = event.target as HTMLButtonElement;
        refreshButton.disabled = true;
        const temp = refreshButton.innerText;
        refreshButton.innerText = "";
        const loader = mount(Loader, {
            target: refreshButton
        })

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

        refreshButton.disabled = false;
        refreshButton.innerText = temp;
        unmount(loader);
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
            <button class = "bg-primary" style="margin-right:5px;" onclick={() => {}}>Delete</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={() => {}}>Move</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={() => {}}>Mark as Important</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={() => {}}>Mark as Not Important</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={markEmailsAsRead}>Mark as Read</button>
            <button class = "bg-primary" style="margin-right:5px;" onclick={() => {}}>Mark as Unread</button>
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
