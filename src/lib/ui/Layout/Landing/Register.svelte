<script lang="ts">
    import { relaunch } from "@tauri-apps/plugin-process";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/ui/Layout/Landing/Register/EditAccountForm.svelte";
    import Loading from "$lib/ui/Layout/Landing/Loading.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { onMount } from "svelte";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { show as showMessage } from "$lib/ui/Components/Message";

    onMount(async () => {
        const response = await AccountController.init();
        if(!response.success) {
            console.error(response.message);
            showMessage({
                title: local.error_initialize_accounts[DEFAULT_LANGUAGE],
            });
        }
    })

    let isLoading = $derived(SharedStore.server === "");
    let editingAccount: Account | null = $state(null);
    let isListingAccount = $state(SharedStore.failedAccounts.length > 0);

    const editAccount = (account: Account) => { editingAccount = account };
    const cancelListing = () => { isListingAccount = false };
    const cancelEditing = () => { editingAccount = null };
</script>

{#if isLoading}
    <Loading />
{:else}
    {#if editingAccount}
        <EditAccountForm {editingAccount} onCancel={cancelEditing}/>
    {:else if isListingAccount}
        <AccountList {editAccount} onCancel={cancelListing} />
    {:else}
        <AddAccountForm onCancel={cancelListing} />
    {/if}
{/if}
