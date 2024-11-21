<script lang="ts">
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import { onMount } from "svelte";
    import type { Response } from "$lib/types";

    let totalEmailCount = $derived(sharedStore.inboxes.reduce(
        (acc, account) => sharedStore.accounts.find((a) => a.email == account.email) ? acc + account.total : acc,
        0,
    ));

    let prevButton: HTMLButtonElement;
    let nextButton: HTMLButtonElement;
    onMount(() => {
        prevButton = document.getElementById(
            "prev-button",
        ) as HTMLButtonElement;
        nextButton = document.getElementById(
            "next-button",
        ) as HTMLButtonElement;

        $effect(() => {
            if (sharedStore.currentOffset >= 10) {
                someFunc();
            }
        })
    });

    async function someFunc(): Promise<void> {
        /**
         * If user moves email to another folder, the offset will not be a multiple of 10.
         * In this case, we need to fetch the emails from the previous page to complete the page.
         * For example, if the offset is 13, we need to fetch the emails from 10 to 20.
         * This is not a good solution but it is enough for now.
         */
        const complete_to_ten = sharedStore.currentOffset - (sharedStore.currentOffset % 10);
        if (complete_to_ten != sharedStore.currentOffset) {
            let response: Response = await fetch(
                `${sharedStore.server}/get-emails/${
                    getCurrentAccountsAsString()
                }?folder=${
                    encodeURIComponent(sharedStore.selectedFolder)
                }&offset=${
                    complete_to_ten.toString()
                }&search=${
                    getSearchMenuValue()
                }`,
            ).then((response) => response.json());
            if (response.success) {
                sharedStore.currentOffset = 10 + complete_to_ten;
                sharedStore.inboxes = response.data.map((item: { email: string; data: object }) => ({
                    email: item.email,
                    ...item.data
                }))
            }
        }
    }

    function getSearchMenuValue() {
        const search = (document.getElementById("search") as HTMLInputElement)
            .value;
        return search.trim() == "" ? "" : search;
    }

    function getCurrentAccountsAsString() {
        return sharedStore.selectedAccounts.map((account) => account.email).join(", ");
    }

    async function getPreviousEmails() {
        if (sharedStore.currentOffset <= 10) return;

        prevButton.disabled = true;
        let response: Response = await fetch(
            `${sharedStore.server}/get-emails/${
                getCurrentAccountsAsString()
            }?folder=${
                encodeURIComponent(sharedStore.selectedFolder)
            }&offset=${
                sharedStore.currentOffset - 20
            }&search=${
                getSearchMenuValue()
            }`,
        ).then((response) => response.json());
        if (response.success) {
            sharedStore.currentOffset = sharedStore.currentOffset - 10;
            sharedStore.inboxes = response.data.map((item: { email: string; data: object }) => ({
                email: item.email,
                ...item.data
            }))
        }
        prevButton.disabled = false;
    }

    async function getNextEmails() {
        if (sharedStore.currentOffset >= totalEmailCount) return;

        nextButton.disabled = true;
        let response: Response = await fetch(
            `${sharedStore.server}/get-emails/${
                getCurrentAccountsAsString()
            }?folder=${
                encodeURIComponent(sharedStore.selectedFolder)
            }&offset=${
                sharedStore.currentOffset
            }&search=${
                getSearchMenuValue()
            }`,
        ).then((response) => response.json());
        if (response.success) {
            sharedStore.currentOffset = sharedStore.currentOffset + 10;
            sharedStore.inboxes = response.data.map((item: { email: string; data: object }) => ({
                email: item.email,
                ...item.data
            }))
        }
        nextButton.disabled = false;
    }
</script>

<section class="card">
    <div class="inbox-header">
        <h2>{sharedStore.selectedFolder == "inbox" ? "Inbox" : sharedStore.selectedFolder}</h2>
        <hr />
        <div class="inbox-pagination">
            <button
                id="prev-button"
                onclick={getPreviousEmails}
                disabled={sharedStore.currentOffset <= 10}>Previous</button>
            <small>{Math.max(1, sharedStore.currentOffset - 9)} - {sharedStore.currentOffset} of {totalEmailCount}</small>
            <button
                id="next-button"
                onclick={getNextEmails}
                disabled={sharedStore.currentOffset >= totalEmailCount}>Next</button>
        </div>
        <hr />
    </div>
    <div class="inbox-content">
      {#each sharedStore.inboxes as account}
        {#if sharedStore.accounts.length == 0 || sharedStore.accounts.find((acc) => acc.email == account.email)}
          {#each account.emails as email}
            <InboxItem owner={account.email} email={email} />
          {/each}
        {/if}
      {/each}
    </div>
</section>

<style>
    .inbox-pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .inbox-content {
        & h3 {
            margin: 0;
        }

        & .inbox-item:first-child {
            padding-top: 0.5rem;
        }

        & .inbox-item:last-child {
            border-bottom: none;
        }
    }
</style>
