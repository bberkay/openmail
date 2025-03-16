<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import { Form, FormGroup } from "$lib/ui/Elements/Form";
    import * as Input from "$lib/ui/Elements/Input";
    import * as Button from "$lib/ui/Elements/Button";
    import Label from "$lib/ui/Elements/Label";

    const accountController = new AccountController();

    interface Props {
        isListingAccount: boolean;
    }

    let { isListingAccount = $bindable() }: Props = $props();

    const addAccount = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);
        const response = await accountController.add(
            formData.get("email_address") as string,
            formData.get("password") as string,
            formData.get("fullname") as string,
        );

        if (!response.success) {
            alert(response.message);
        }
    };
</script>

<Form onsubmit={addAccount}>
    <div>
        <FormGroup>
            <Label for="email_address">Email Address</Label>
            <Input.Basic
                type="email"
                name="email_address"
                id="email_address"
                placeholder="alexdoe@gmail.com"
                autocomplete="off"
                autofocus
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
            />
            <span class="muted">Example: Alex Doe &lt;alex.doe@openmail.com&gt;</span>
        </FormGroup>
        <Button.Action
            type="submit"
            id="add-account-btn"
            onclick={async (e): Promise<void> => { addAccount(e) }}
        >
            Connect to accounts.
        </Button.Action>
        <div class="list-accounts-navigation">
            <Button.Basic
                type="button"
                class="inline"
                onclick={() => { isListingAccount = true; }}
            >
                Which accounts have I added?
            </Button.Basic>
        </div>
    </div>
</Form>

<style>
    .list-accounts-navigation {
        text-align: center;
        margin-top: 20px;
    }
</style>
