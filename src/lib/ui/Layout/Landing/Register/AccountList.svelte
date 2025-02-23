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

    const removeAccount = async (e: Event): Promise<void> => {
        const target = e.target as HTMLButtonElement;
        const account = target.getAttribute("data-email-address")!;
        const response = await accountController.remove(account);

        if (!response.success) {
            alert(response.message);
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

    const removeAllFailedAccounts = async (): Promise<void> => {
        if (
            confirm(
                "Are you certain? You are about to remove all failed accounts.",
            )
        ) {
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    };
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
                <th><input type="checkbox"></th>
                <th>Account Email Address</th>
                <th colspan="2"></th>
            </tr>
        </thead>
        <tbody>
            {#each SharedStore.failedAccounts.concat(SharedStore.accounts) as account, index}
            <tr class={index < failedAccountLength ? "failed" : ""}>
                <td><input type="checkbox"></td>
                <td>
                    {index < failedAccountLength ? "Warning" : ""}
                    {account.fullname} &lt;{account.email_address}&gt;
                </td>
                <td>
                    <button
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

        & th {
            text-align: left;
        }

        & th, & td{
            border:1px solid #444;
            padding: 0.5em;
            padding-left: 0.75em;
        }
    }
</style>
