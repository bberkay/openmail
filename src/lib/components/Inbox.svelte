<script lang="ts">
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import { onMount } from "svelte";
    import type { Account } from "$lib/types";
    import { ApiService, GetRoutes, type Response } from "$lib/services/ApiService";

    let totalEmailCount = $derived(0);

    let prevButton: HTMLButtonElement;
    let nextButton: HTMLButtonElement;
    onMount(() => {
        prevButton = document.getElementById(
            "prev-button",
        ) as HTMLButtonElement;
        nextButton = document.getElementById(
            "next-button",
        ) as HTMLButtonElement;

        /*$effect(() => {
            if (sharedStore.currentOffset >= 10) {
                completeToTen();
            }
        })*/
    });

    async function completeToTen(): Promise<void> {
        const missing = sharedStore.currentOffset - (sharedStore.currentOffset % 10);
        if (missing != sharedStore.currentOffset) {
            let response: Response = await ApiService.get(
                sharedStore.server,
                GetRoutes.GET_EMAILS,
                {
                    pathParams: {
                        accounts: getCurrentAccountsAsString()

                    },
                    queryParams: {
                        folder: encodeURIComponent(sharedStore.selectedFolder),
                        offset_start: missing,
                        offset_end: missing + 10,
                        search: getSearchMenuValue()
                    }
                }
            );

            if (response.success) {
                sharedStore.currentOffset = 10 + missing;
                sharedStore.mailboxes = response.data.map((item: { email_adress: string; data: object }) => ({
                    email_adress: item.email_adress,
                    ...item.data
                }))
            }
        }
    }

    function getSearchMenuValue() {
        return "ALL";
    }

    function getCurrentAccountsAsString() {
        return sharedStore.selectedAccounts.map((account) => account.email_address).join(", ");
    }

    async function getPreviousEmails() {
        if (sharedStore.currentOffset <= 10)
            return;

        prevButton.disabled = true;
        let response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_EMAILS,
            {
                pathParams: {
                    accounts: getCurrentAccountsAsString(),
                },
                queryParams: {
                    folder: encodeURIComponent(sharedStore.selectedFolder),
                    offset_start: (Math.max(0, sharedStore.currentOffset - 20)),
                    offset_end: (sharedStore.currentOffset - 10),
                    search: getSearchMenuValue()
                }
            }
        );

        if (response.success) {
            sharedStore.currentOffset = sharedStore.currentOffset - 10;
            sharedStore.mailboxes = response.data.map((item: { email: string; data: object }) => ({
                email: item.email,
                ...item.data
            }))
        }

        prevButton.disabled = false;
    }

    async function getNextEmails() {
        if (sharedStore.currentOffset >= totalEmailCount)
            return;

        nextButton.disabled = true;
        let response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_EMAILS,
            {
                pathParams: {
                    accounts: getCurrentAccountsAsString(),
                },
                queryParams: {
                    folder: encodeURIComponent(sharedStore.selectedFolder),
                    offset_start: (sharedStore.currentOffset + 10),
                    offset_end: (sharedStore.currentOffset + 20),
                    search: getSearchMenuValue()
                }
            }
        );

        if (response.success) {
            sharedStore.currentOffset = sharedStore.currentOffset + 10;
            sharedStore.mailboxes = response.data.map((item: { email_adress: string; data: object }) => ({
                email_address: item.email_adress,
                ...item.data
            }))
        }

        nextButton.disabled = false;
    }
</script>

<section>
    <div>
        <h2>{sharedStore.selectedFolder}</h2>
        <hr />
        <div>
            <button id="prev-button" onclick={getPreviousEmails} disabled={sharedStore.currentOffset <= 10}>
                Previous
            </button>
            <small>
                {Math.max(1, sharedStore.currentOffset - 9)} - {sharedStore.currentOffset} of {totalEmailCount}
            </small>
            <button id="next-button" onclick={getNextEmails} disabled={sharedStore.currentOffset >= totalEmailCount}>
                Next
            </button>
        </div>
        <hr />
    </div>
    <div>
        {#each sharedStore.mailboxes as mailbox}
            {#each mailbox.data.emails as email}
              <InboxItem owner={mailbox.email_address} email={email} />
            {/each}
        {/each}
      <!--{#each sharedStore.mailboxes as mailbox}
        {#if sharedStore.accounts.find((acc: Account) => acc.email_address == mailbox.email_address)}
          {#each mailbox.mailbox.emails as email}
            <InboxItem owner={mailbox.email_address} email={email} />
          {/each}
        {/if}
      {/each}-->
    </div>
</section>
