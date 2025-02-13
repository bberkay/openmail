<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account } from "$lib/types";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/ui/Layout/Landing/Register/EditAccountForm.svelte";
    import * as Button from "$lib/ui/Elements/Button";

    const mailboxController = new MailboxController();

    let editingAccount: Account | null = $state(SharedStore.failedAccounts
        ? SharedStore.failedAccounts[0]
        : null);

    async function initMailboxes(): Promise<void> {
        const response = await mailboxController.init();
        if (!response.success) {
            alert(response.message);
        } else {
            SharedStore.currentAccount = null;
            SharedStore.currentFolder = Folder.Inbox;
        }
    }
</script>

{#if editingAccount}
    <h3>Edit Account</h3>
    <EditAccountForm bind:editingAccount={editingAccount}/>
{:else}
    <h3>Add Account</h3>
    <AddAccountForm />
{/if}

<AccountList bind:editingAccount={editingAccount}/>

{#if SharedStore.accounts.length > 0}
<div>
    <Button.Action onclick={initMailboxes}>
        Continue To Inbox
    </Button.Action>
</div>
{/if}
