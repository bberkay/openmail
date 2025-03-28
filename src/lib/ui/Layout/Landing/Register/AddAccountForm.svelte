<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import Form from "$lib/ui/Components/Form";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        onCancel: () => void;
    }

    let { onCancel }: Props = $props();

    const addAccount = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);
        const response = await AccountController.add(
            formData.get("email_address") as string,
            formData.get("password") as string,
            formData.get("fullname") as string,
        );

        if (!response.success) {
            showMessage({content: "Error while adding account."});
            console.error(response.message);
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
                autocomplete="off"
            />
            <span class="muted">Example: Alex Doe &lt;alex.doe@openmail.com&gt;</span>
        </FormGroup>
        <div class="landing-body-footer">
            <Button.Basic type="submit">
                Connect to account.
            </Button.Basic>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={onCancel}
            >
                Which accounts have I added?
            </Button.Basic>
        </div>
    </div>
</Form>
