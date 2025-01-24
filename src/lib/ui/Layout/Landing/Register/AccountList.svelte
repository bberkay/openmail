<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { type Account } from "$lib/types";

    const accountController = new AccountController();

    interface Props {
        editingAccount: Account | null;
    }

    let { editingAccount = $bindable() }: Props = $props();

    const removeAccount = async (e: Event): Promise<void> => {
        const target = e.target as HTMLButtonElement;
        const account = target.getAttribute('data-email-address')!
        const response = await accountController.remove(account);

        if (!response.success) {
            alert(response.message);
        }
    }

    const removeAllAccounts = async (): Promise<void> => {
        if(confirm("Are you certain? You are about to remove all accounts.")){
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    }

    const removeAllFailedAccounts = async (): Promise<void> => {
        if(confirm("Are you certain? You are about to remove all failed accounts.")){
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    }
</script>

{#if SharedStore.accounts && SharedStore.accounts.length > 0}
    <h3>Current Accounts <button onclick={removeAllAccounts}>Remove All</button></h3>
    <ul>
        {#each SharedStore.accounts as account}
            <li>
                <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                <button style="margin-right: 5px;" onclick={() => { editingAccount = account }}>Edit</button>
                <ActionButton onclick={removeAccount} data-email-address={account.email_address} >
                    Remove
                </ActionButton>
            </li>
        {/each}
    </ul>
    {#if SharedStore.failedAccounts.length > 0}
        <h3>Failed Accounts <button onclick={removeAllFailedAccounts}>Remove All</button></h3>
        <small>There were {SharedStore.failedAccounts.length} accounts that failed to connect.</small>
        {#each SharedStore.failedAccounts as failedAccount}
            <li>
                <span style="margin-right: 5px;">{failedAccount.fullname} &lt;{failedAccount.email_address}&gt;</span>
                <button style="margin-right: 5px;" onclick={() => { editingAccount = failedAccount }}>Edit</button>
                <ActionButton onclick={removeAccount} data-email-address={failedAccount.email_address} >
                    Remove
                </ActionButton>
            </li>
        {/each}
    {/if}
{/if}
