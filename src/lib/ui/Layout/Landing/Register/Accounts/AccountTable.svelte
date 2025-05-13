<script lang="ts">
    import Header from "./AccountTable/Header.svelte";
    import Table from "./AccountTable/Table.svelte";
    import Pagination from "./AccountTable/Pagination.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";

    interface Props {
        accountsPerPage: number;
        showEditAccount: (account: Account) => void;
        onRemoveAccount?: (email_address: string) => Promise<void>;
    }

    let {
        accountsPerPage,
        showEditAccount,
        onRemoveAccount,
    }: Props = $props();

    let allAccounts = $derived(
        SharedStore.failedAccounts.concat(SharedStore.accounts),
    );
    let shownAccounts = $derived(allAccounts.slice(0, accountsPerPage));
    let accountSelection: string[] = $state([]);
    let accountSelectionType: "shown" | "all" | "parts" = $state("parts");
</script>

<Header
    bind:allAccounts
    bind:shownAccounts
    bind:accountSelection
    bind:accountSelectionType
/>
<Table
    bind:shownAccounts
    bind:accountSelection
    bind:accountSelectionType
    {showEditAccount}
    {onRemoveAccount}
/>
<Pagination
    bind:allAccounts
    bind:shownAccounts
    {accountsPerPage}
/>
