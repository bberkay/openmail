<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Form from "$lib/components/Elements/Form.svelte";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { AccountEvent, type Account } from "$lib/types";
    import { onMount, onDestroy } from "svelte";

    const accountController = new AccountController();

    let currentEditingAccount: Account | null = $state(
        SharedStore.failedAccounts
            ? SharedStore.failedAccounts[0]
            : null
    );

    function handleEditingAccount(event: CustomEvent) {
        currentEditingAccount = event.detail.account;
    }

    onMount(() => {
        document.addEventListener(AccountEvent.onEditingAccount, handleEditingAccount as EventListener);
    });

    onDestroy(() => {
        document.removeEventListener(AccountEvent.onEditingAccount, handleEditingAccount as EventListener);
    });

    $effect(() => {
        if (!currentEditingAccount && SharedStore.failedAccounts.length > 0)
            currentEditingAccount = SharedStore.failedAccounts[0];
    });

    const editAccount = async (form: HTMLFormElement): Promise<void> => {
        const formData = new FormData(form);
        const response = await accountController.edit(
            formData.get('email_address') as string,
            formData.get('fullname') as string,
            formData.get("password") as string
        );

        if(!response.success){
            alert(response.message);
        }
    }

    const removeAccount = async (e: Event): Promise<void> => {
        const target = e.target as HTMLButtonElement;
        const account = target.getAttribute('data-email-address')!
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

    const cancelEdit = () => {
        currentEditingAccount = null;
    }
</script>

<Form Inner={EditAccountForm} operation={editAccount} />

{#snippet EditAccountForm()}
    {#if currentEditingAccount}
        <div>
            <h3>Updating Accounts <button onclick={removeAllAccounts}>Remove All</button></h3>
            <small>There were {SharedStore.failedAccounts.length} accounts that failed to connect.</small>
            <ul>
                {#each SharedStore.failedAccounts as account}
                    <li>
                        <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                        <button style="margin-right: 5px;" onclick={() => { currentEditingAccount = account }}>Edit</button>
                        <ActionButton onclick={removeAccount}  data-email-address={currentEditingAccount.email_address} >
                            Remove
                        </ActionButton>
                        </li>
                    {/each}
                </ul>
            <hr>
            <div>
                <label for="email_address">Email Address</label><br>
                <input type="email" name="email_address" id="email_address" autocomplete="off" placeholder="someone@domain.xyz" value="{currentEditingAccount.email_address}" readonly required>
                </div>
            <div>
                <label for="password">Password</label><br>
                    <!-- svelte-ignore a11y_autofocus -->
                <input type="password" name="password" id="password" autocomplete="off" autofocus required>
                </div>
            <div>
                <label for="fullname">Fullname (Optional)</label><br>
                <input type="text" name="fullname" id="fullname" autocomplete="off" placeholder="Fullname" value="{currentEditingAccount.fullname}"><br>
                <small style="font-style:italic;margin-top:5px;">Enter your fullname to be displayed in the email.</small>
                </div>
            <button type="submit" id="edit-account-btn">Edit Account</button>
            <button type="button" onclick={cancelEdit}>Cancel</button>
            <ActionButton onclick={removeAccount} data-email-address={currentEditingAccount.email_address}>
                Remove
            </ActionButton>
        </div>
    {/if}
{/snippet}
