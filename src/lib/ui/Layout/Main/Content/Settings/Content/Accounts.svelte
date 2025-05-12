<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import AccountTable from "$lib/ui/Layout/Landing/Register/AccountList/AccountTable.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import EditAccountForm from "./Accounts/AddAccountForm.svelte";

    const ACCOUNTS_PER_PAGE = 15;

    const showEditAccount = () => {
        showModal(EditAccountForm);
    };

    const onRemoveAccount = async (email_address: string) => {
        if (Object.hasOwn(SharedStore.notificationChannels, email_address)) {
            SharedStore.notificationChannels[email_address].terminate();
            delete SharedStore.notificationChannels[email_address];
        }
    }
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">Accounts</h1>
    <span class="settings-content-description muted">These are accounts settings.</span>
</div>
<div class="settings-content-body">
    <!-- TODO: Add account form, and failed accounts alert uncloseable --->
    <AccountTable
        accountsPerPage={ACCOUNTS_PER_PAGE}
        {showEditAccount}
        {onRemoveAccount}
    />
</div>
