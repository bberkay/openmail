<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/ui/Layout/Landing/Register/EditAccountForm.svelte";
    import Loading from "$lib/ui/Layout/Landing/Loading.svelte";

    let isLoading = $derived(SharedStore.server === "");
    let editingAccount: Account | null = $state(null);
    let isListingAccount = $state(SharedStore.failedAccounts.length > 0);

    const cancelListing = () => { isListingAccount = false };
    const cancelEditing = () => { editingAccount = null };
</script>

{#if isLoading}
    <Loading />
{:else}
    {#if editingAccount}
        <EditAccountForm editingAccount={editingAccount} onCancel={cancelEditing}/>
    {:else if isListingAccount}
        <AccountList bind:editingAccount onCancel={cancelListing} />
    {:else}
        <AddAccountForm onCancel={cancelListing} />
    {/if}
{/if}
