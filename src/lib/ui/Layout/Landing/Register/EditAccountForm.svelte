<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { type Account } from "$lib/types";
    import Form from "$lib/ui/Elements/Form";
    import * as Input from "$lib/ui/Elements/Input";

    const accountController = new AccountController();

    interface Props {
        isEditingAccount: Account | null;
    }

    let { isEditingAccount = $bindable() }: Props = $props();

    $effect(() => {
        if (!isEditingAccount && SharedStore.failedAccounts.length > 0)
            isEditingAccount = SharedStore.failedAccounts[0];
    });

    const editAccount = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);
        const response = await accountController.edit(
            formData.get("email_address") as string,
            formData.get("password") as string,
            formData.get("fullname") as string,
        );

        if (!response.success) {
            alert(response.message);
        }
    };
</script>

{#if isEditingAccount}
    <Form onsubmit={editAccount}>
        <div>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input
                    type="email"
                    name="email_address"
                    id="email_address"
                    autocomplete="off"
                    value={isEditingAccount.email_address}
                    readonly
                    required
                />
            </div>
            <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <Input.Password/>
            </div>
            <div class="form-group">
                <label for="fullname" class="form-label">Full Name (Optional)</label>
                <input type="text" name="fullname" id="fullname" placeholder="Alex Doe" class="form-input" autocomplete="off" value={isEditingAccount.fullname}>
                <p class="hint">Example: Alex Doe &lt;alex.doe@openmail.com&gt;</p>
            </div>
            <button type="submit" id="edit-account-btn" style="margin-right:10px;">Edit Account</button>
            <button type="button" class="inline" onclick={() => { isEditingAccount = null; }}>
                Cancel
            </button>
        </div>
    </Form>
{/if}
