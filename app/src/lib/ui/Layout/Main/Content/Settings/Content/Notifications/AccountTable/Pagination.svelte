<script lang="ts">
    import type { Account } from "$lib/types";
    import * as Pagination from "$lib/ui/Components/Pagination";

    interface Props {
        allAccounts: Account[];
        shownAccounts: Account[];
        accountsPerPage: number;
    }

    let {
        allAccounts = $bindable(),
        shownAccounts = $bindable(),
        accountsPerPage
    }: Props = $props();

    const updateAccountPage = (newOffset: number) => {
        shownAccounts = allAccounts.slice(
            newOffset - accountsPerPage,
            newOffset,
        );
    };
</script>

{#if allAccounts.length > accountsPerPage}
    <div class="account-list-pagination-container">
        <Pagination.Pages
            total={allAccounts.length}
            onChange={updateAccountPage}
            offsetStep={accountsPerPage}
        />
    </div>
{/if}
