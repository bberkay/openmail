<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import AccountTable from "$lib/ui/Layout/Landing/Register/AccountList/AccountTable.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import EditAccountForm from "./EditAccountForm.svelte";
    import AddAccountForm from "./AddAccountForm.svelte";
    import type { Account } from "$lib/types";

    const ACCOUNTS_PER_PAGE = 5;

    const showAddAccount = () => {
        showModal(AddAccountForm);
    };

    const showEditAccount = (account: Account) => {
        showModal(EditAccountForm, { account });
    };

    const onRemoveAccount = async (email_address: string) => {
        if (Object.hasOwn(SharedStore.notificationChannels, email_address)) {
            SharedStore.notificationChannels[email_address].terminate();
            delete SharedStore.notificationChannels[email_address];
        }
    }
</script>

<!-- TODO: Implement add account form -->
<AccountTable
    accountsPerPage={ACCOUNTS_PER_PAGE}
    {showEditAccount}
    {onRemoveAccount}
/>
