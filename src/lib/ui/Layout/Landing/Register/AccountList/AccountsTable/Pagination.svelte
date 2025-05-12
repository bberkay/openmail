<script lang="ts">
    import type { Account } from "$lib/types";
    import * as Pagination from "$lib/ui/Components/Pagination";

    interface Props {
        allAccounts: Account[];
        accounts: Account[];
        accountsPerPage: number;
    }

    let {
        allAccounts = $bindable(),
        accounts = $bindable(),
        accountsPerPage
    }: Props = $props();

    const updateAccountPage = (newOffset: number) => {
        accounts = allAccounts.slice(
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

<style>
    :global {
        .account-list-pagination-container {
            margin-top: var(--spacing-md);
        }
    }
</style>
