<script lang="ts">
    import Header from "./AccountsTable/Header.svelte";
    import Table from "./AccountsTable/Table.svelte";
    import Pagination from "./AccountsTable/Pagination.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";

    interface Props {
        accountsPerPage: number;
        showEditAccount: (account: Account) => void;
        onRemoveAccount?: (email_address: string) => Promise<void>;
        onRemoveAllAccounts?: () => Promise<void>;
    }

    let {
        accountsPerPage,
        showEditAccount,
        onRemoveAccount,
        onRemoveAllAccounts
    }: Props = $props();

    let allAccounts = $derived(
        SharedStore.failedAccounts.concat(SharedStore.accounts),
    );
    let accounts = $derived(allAccounts.slice(0, accountsPerPage));
    let accountSelection: string[] = $state([]);
    let accountSelectionType: "shown" | "all" | false = $state(false);
</script>

<Header
    bind:allAccounts
    bind:accounts
    bind:accountSelection
    bind:accountSelectionType
/>
<Table
    bind:accounts
    bind:accountSelection
    bind:accountSelectionType
    {showEditAccount}
    {onRemoveAccount}
    {onRemoveAllAccounts}
/>
<Pagination
    bind:allAccounts
    bind:accounts
    {accountsPerPage}
/>
