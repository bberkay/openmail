<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Form from "$lib/components/Elements/Form.svelte";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { type Account } from "$lib/types";

    const accountController = new AccountController();

    interface Props {
        editingAccount: Account | null;
    }

    let { editingAccount = $bindable() }: Props = $props();

    $effect(() => {
        if (!editingAccount && SharedStore.failedAccounts.length > 0)
            editingAccount = SharedStore.failedAccounts[0];
    });

    const editAccount = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);
        const response = await accountController.edit(
            formData.get('email_address') as string,
            formData.get("password") as string,
            formData.get('fullname') as string
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

    const cancelEdit = () => {
        editingAccount = null;
    }
</script>

{#if editingAccount}
    <Form onsubmit={editAccount}>
        <div>
            <div>
                <label for="email_address">Email Address</label><br>
                <input type="email" name="email_address" id="email_address" autocomplete="off" placeholder="someone@domain.xyz" value="{editingAccount.email_address}" readonly required>
            </div>
            <div>
                <label for="password">Password</label><br>
                    <!-- svelte-ignore a11y_autofocus -->
                <input type="password" name="password" id="password" autocomplete="off" autofocus required>
            </div>
            <div>
                <label for="fullname">Fullname (Optional)</label><br>
                <input type="text" name="fullname" id="fullname" autocomplete="off" placeholder="Fullname" value="{editingAccount.fullname}"><br>
                <small style="font-style:italic;margin-top:5px;">Enter your fullname to be displayed in the email.</small>
            </div>
            <button type="submit" id="edit-account-btn">Edit Account</button>
            <button type="button" onclick={cancelEdit}>Cancel</button>
            <ActionButton onclick={removeAccount} data-email-address={editingAccount.email_address}>
                Remove
            </ActionButton>
        </div>
    </Form>
{/if}
