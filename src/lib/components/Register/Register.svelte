<script lang="ts">
    import AccountList from "$lib/components/Register/AccountList.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import AddAccountForm from "$lib/components/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/components/Register/EditAccountForm.svelte";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

    const mailboxController = new MailboxController();

    async function getFoldersOfAllAccounts() {
        const response = await mailboxController.getAllFolders();
        if (!response.success) {
            alert(response.message);
        }
    }

    async function getMailboxesOfAllAccounts() {
        const response = await mailboxController.getAllMailboxes();
        if (!response.success) {
            alert(response.message);
        }
    }

    async function continueToInbox(): Promise<void> {
        await getFoldersOfAllAccounts();
        await getMailboxesOfAllAccounts();
    }
</script>

{#if SharedStore.failedAccounts.length > 0}
    <h3>Edit Account</h3>
    <EditAccountForm />
{:else}
    <h3>Add Account</h3>
    <AddAccountForm />
{/if}

<AccountList/>

<div>
    <ActionButton onclick={continueToInbox}>
        Continue To Inbox
    </ActionButton>
</div>
