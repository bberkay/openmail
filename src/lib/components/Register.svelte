<script lang="ts">
    import AccountList from "$lib/components/Register/AccountList.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import AddAccountForm from "./Register/AddAccountForm.svelte";
    import EditAccountForm from "./Register/EditAccountForm.svelte";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

    const mailboxController = new MailboxController();

    async function getFoldersOfAllAccounts() {
        const response = await mailboxController.updateAllFolders();
        if (!response.success) {
            alert(response.message);
        }
    }

    async function getMailboxesOfAllAccounts() {
        const response = await mailboxController.updateAllMailboxes();
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
    <ActionButton id="continue-to-inbox" operation={continueToInbox} inner="Continue To Inbox" />
</div>
