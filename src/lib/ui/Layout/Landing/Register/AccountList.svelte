<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { type Account } from "$lib/types";
    import * as Button from "$lib/ui/Elements/Button";

    const accountController = new AccountController();

    interface Props {
        isEditingAccount: Account | null;
    }

    let { isEditingAccount = $bindable() }: Props = $props();
    let accountSelection: string[] = $state([]);

    const removeAccount = async (e: Event): Promise<void> => {
        if (confirm("Are you certain? Deleting an account cannot be undone.")) {
            const target = e.target as HTMLButtonElement;
            const account = target.getAttribute("data-email-address")!;
            const response = await accountController.remove(account);

            if (!response.success) {
                alert(response.message);
            }
        }
    };

    const removeAllAccounts = async (): Promise<void> => {
        if (confirm("Are you certain? You are about to remove all accounts.")) {
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    };

    const selectAllAccounts = (event: Event) => {
        const selectAllCheckbox = event.target as HTMLInputElement;
        accountSelection = selectAllCheckbox.checked
            ? SharedStore.failedAccounts.concat(SharedStore.accounts).map((account) => account.email_address)
            : [];
    }
</script>

<div>
    {#if SharedStore.failedAccounts.length > 0}
        <div class="alert">
            <span>
                There were {SharedStore.failedAccounts.length} accounts that failed to
                connect.
            </span>
        </div>
    {/if}
    {#if
        (SharedStore.accounts && SharedStore.accounts.length > 0)
        || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)
    }
    {@const failedAccountLength = SharedStore.failedAccounts.length}
    <table class="account_list--table">
        <thead>
            <tr>
                <th><input type="checkbox" onclick={selectAllAccounts}></th>
                <th>Account{accountSelection.length > 0 ? ` (${accountSelection.length} selected)` : ""}</th>
                <th colspan="2">
                    {#if accountSelection.length > 0}
                        <Button.Action
                            class="inline"
                            onclick={removeAllAccounts}
                        >
                            Remove All
                        </Button.Action>
                    {:else}
                        <Button.Action
                            class="inline"
                            style="visibility: hidden;"
                            onclick={() => {}}
                        >
                            invisible
                        </Button.Action>
                    {/if}
                </th>
            </tr>
        </thead>
        <tbody>
            {#each SharedStore.failedAccounts.concat(SharedStore.accounts) as account, index}
            <tr class={index < failedAccountLength ? "failed" : ""}>
                <td><input type="checkbox" bind:group={accountSelection} value={account.email_address}></td>
                <td>
                    {index < failedAccountLength ? "Warning" : ""}
                    {account.fullname} &lt;{account.email_address}&gt;
                </td>
                <td>
                    <button
                        class="inline"
                        style="margin-right: 5px;"
                        onclick={() => {
                            isEditingAccount = account;
                        }}
                    >
                        Edit
                    </button>
                </td>
                <td>
                    <Button.Action
                        class="inline"
                        onclick={removeAccount}
                        data-email-address={account.email_address}
                    >
                        Remove
                    </Button.Action>
                </td>
            </tr>
            {/each}
        </tbody>
    </table>
    {/if}
</div>

<style>
    .account_list--table{
        background-color: #222;
        width: 100%;
        border-collapse: collapse;

        & th, & td{
            border:1px solid #444;
            padding: 0.85em 0.5em;
            padding-bottom: 0.65em;
            text-align: center;
        }
    }

    .account_list--table th:nth-child(2),
    .account_list--table td:nth-child(2) {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: left;
    }
</style>
