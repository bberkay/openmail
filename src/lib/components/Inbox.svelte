<script lang="ts">
    import InboxItem from "./Inbox/InboxItem.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { onMount } from "svelte";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";

    let totalEmailCount = $derived(SharedStore.mailboxes.reduce((a, b) => a + b.result.total, 0));
    let currentOffset = $state(1);

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
            if (currentOffset >= 10) {
                completeToTen();
            }
        })*/
    });

    async function completeToTen(): Promise<void> {
        const missing = currentOffset - (currentOffset % 10);
        if (missing != currentOffset) {
            const response = await ApiService.get(
                SharedStore.server,
                GetRoutes.GET_MAILBOXES,
                {
                    pathParams: {
                        accounts: getCurrentAccountsAsString()

                    },
                    queryParams: {
                        folder: encodeURIComponent(SharedStore.selectedFolder),
                        offset_start: missing,
                        offset_end: missing + 10,
                        search: getSearchMenuValue()
                    }
                }
            );

            if (response.success && response.data) {
                currentOffset = 10 + missing;
                SharedStore.mailboxes = response.data;
            }
        }
    }

    function getSearchMenuValue() {
        return "ALL";
    }

    function getCurrentAccountsAsString() {
        return SharedStore.accounts.map((account) => account.email_address).join(", ");
    }

    async function getPreviousEmails() {
        if (currentOffset <= 10)
            return;

        prevButton.disabled = true;
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: getCurrentAccountsAsString(),
                    offset_start: (Math.max(0, currentOffset - 10)),
                    offset_end: (Math.max(0, currentOffset)),
                }
            }
        );

        if (response.success && response.data) {
            currentOffset = Math.max(0, currentOffset - 10);
            SharedStore.mailboxes = response.data;
        }

        prevButton.disabled = false;
    }

    async function getNextEmails() {
        if (currentOffset >= totalEmailCount)
            return;

        nextButton.disabled = true;
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: getCurrentAccountsAsString(),
                    offset_start: Math.min(totalEmailCount, currentOffset + 10),
                    offset_end: Math.min(totalEmailCount, currentOffset + 10 + 10)
                }
            }
        );

        if (response.success && response.data) {
            currentOffset = Math.min(totalEmailCount, currentOffset + 10);
            SharedStore.mailboxes = response.data;
        }

        nextButton.disabled = false;
    }
</script>

<section>
    <div>
        <h2>{SharedStore.selectedFolder}</h2>
        <hr />
        <div>
            <button id="prev-button" class = "bg-primary" onclick={getPreviousEmails} disabled={currentOffset <= 10}>
                Previous
            </button>
            <small>
                {Math.max(1, currentOffset)} - {Math.min(totalEmailCount, currentOffset + 10)} of {totalEmailCount}
            </small>
            <button id="next-button" class = "bg-primary" onclick={getNextEmails} disabled={currentOffset >= totalEmailCount}>
                Next
            </button>
        </div>
        <hr />
    </div>
    <div>
        {#each SharedStore.mailboxes as account}
            {#each account.result.emails as email}
              <InboxItem owner={account.email_address} email={email} />
            {/each}
        {/each}
    </div>
</section>
