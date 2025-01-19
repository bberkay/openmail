<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { type Account, AccountEvent } from "$lib/types";

    const accountController = new AccountController();

    const removeAccount = async (eventTrigger: HTMLButtonElement): Promise<void> => {
        const account = eventTrigger.getAttribute('data-email-address')!
        const response = await accountController.remove(account);

        if (!response.success) {
            alert(response.message);
        }
    }

    const removeAllAccounts = async (): Promise<void> => {
        if(confirm("Are you certain?")){
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    }

    const dispatchEditAccount = (account: Account) => {
        document.dispatchEvent(
            new CustomEvent(AccountEvent.onEditingAccount, {
                detail: { account },
            })
        );
    }
</script>

{#if SharedStore.accounts && SharedStore.accounts.length > 0}
    <h3>Current Accounts <button onclick={removeAllAccounts}>Remove All</button></h3>
    <ul>
        {#each SharedStore.accounts as account}
            <li>
                <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                <button style="margin-right: 5px;" onclick={() => { dispatchEditAccount(account) }}>Edit</button>
                <ActionButton id="remove-account" operation={removeAccount} data-email-address={account.email_address} >
                    Remove
                </ActionButton>
            </li>
        {/each}
    </ul>
{/if}
