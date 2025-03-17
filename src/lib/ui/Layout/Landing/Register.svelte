<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/ui/Layout/Landing/Register/EditAccountForm.svelte";
    import Loading from "$lib/ui/Layout/Landing/Loading.svelte";

    let isLoading: boolean = $derived(SharedStore.server === "");
    let isEditingAccount: Account | null = $state(null);
    let isListingAccount: boolean = $state(SharedStore.failedAccounts.length > 0);
</script>

{#if isLoading}
    <Loading />
{:else}
    {#if isEditingAccount}
        <EditAccountForm bind:isEditingAccount />
    {:else if isListingAccount}
        <AccountList bind:isEditingAccount bind:isListingAccount />
    {:else}
        <AddAccountForm bind:isListingAccount />
    {/if}
{/if}
