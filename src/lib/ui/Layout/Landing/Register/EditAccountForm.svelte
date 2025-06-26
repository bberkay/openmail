<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import { type Account } from "$lib/types";
    import Form from "$lib/ui/Components/Form";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { showThis as showContent } from "$lib/ui/Layout/Landing/Register.svelte";
    import Accounts from "$lib/ui/Layout/Landing/Register/Accounts.svelte";

    interface Props {
        account: Account;
    }

    let { account }: Props = $props();

    const editAccount = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);
        const response = await AccountController.edit(
            formData.get("email_address") as string,
            formData.get("password") as string,
            formData.get("fullname") as string,
        );

        if (!response.success) {
            showMessage({ title: local.error_edit_account[DEFAULT_LANGUAGE] });
            console.error(response.message);
        }
    };

    const cancelEdit = () => {
        showContent(Accounts);
    };
</script>

<Form onsubmit={editAccount}>
    <FormGroup>
        <Label for="email_address">
            {local.email_address[DEFAULT_LANGUAGE]}
        </Label>
        <Input.Basic
            type="email"
            name="email_address"
            id="email_address"
            value={account.email_address}
            autocomplete="off"
            readonly
            required
        />
    </FormGroup>
    <FormGroup>
        <Label for="password">{local.password[DEFAULT_LANGUAGE]}</Label>
        <Input.Password />
    </FormGroup>
    <FormGroup>
        <Label for="fullname">
            {local.full_name_optional[DEFAULT_LANGUAGE]}
        </Label>
        <Input.Basic
            type="text"
            name="fullname"
            id="fullname"
            placeholder={local.full_name_placeholder[DEFAULT_LANGUAGE]}
            value={account.fullname}
            autocomplete="off"
        />
        <span class="muted">{local.full_name_example[DEFAULT_LANGUAGE]}</span>
    </FormGroup>
    <div class="landing-body-footer">
        <Button.Basic type="submit" class="btn-cta">
            {local.connect_to_account[DEFAULT_LANGUAGE]}
        </Button.Basic>
        <Button.Basic type="button" class="btn-inline" onclick={cancelEdit}>
            {local.cancel[DEFAULT_LANGUAGE]}
        </Button.Basic>
    </div>
</Form>
