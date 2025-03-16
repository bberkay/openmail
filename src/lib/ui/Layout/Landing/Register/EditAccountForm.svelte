<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { type Account } from "$lib/types";
    import Form from "$lib/ui/Elements/Form";
    import { FormGroup } from "$lib/ui/Elements/Form";
    import * as Input from "$lib/ui/Elements/Input";
    import * as Button from "$lib/ui/Elements/Button";
    import Label from "$lib/ui/Elements/Label";

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
            <FormGroup>
                <Label for="email_address">Email Address</Label>
                <Input.Basic
                    type="email"
                    name="email_address"
                    id="email_address"
                    value={isEditingAccount.email_address}
                    autocomplete="off"
                    readonly
                    required
                />
            </FormGroup>
            <FormGroup>
                <Label for="password">Password</Label>
                <Input.Password/>
            </FormGroup>
            <FormGroup>
                <Label for="fullname">Full Name (Optional)</Label>
                <Input.Basic
                    type="text"
                    name="fullname"
                    id="fullname"
                    placeholder="Alex Doe"
                    value={isEditingAccount.fullname}
                    autocomplete="off"
                />
                <span class="muted">Example: Alex Doe &lt;alex.doe@openmail.com&gt;</span>
            </FormGroup>
            <div class="landing-body-footer">
                <Button.Action
                    type="submit"
                    onclick={async (e): Promise<void> => { editAccount(e) }}
                >
                    Connect to account
                </Button.Action>
                <Button.Basic
                    type="button"
                    class="inline"
                    onclick={() => { isEditingAccount = null; }}
                >
                    Cancel
                </Button.Basic>
            </div>
        </div>
    </Form>
{/if}
