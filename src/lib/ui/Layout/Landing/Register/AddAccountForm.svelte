<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import Form from "$lib/ui/Elements/Form";
    import * as Input from "$lib/ui/Elements/Input";

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
        <div class="form-group">
            <label for="email_address" class="form-label">Email Address</label>
            <!-- svelte-ignore a11y_autofocus -->
            <input type="email" name="email_address" id="email_address" placeholder="alexdoe@domain.com" class="form-input" autofocus autocomplete="off" required>
        </div>
        <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <Input.Password/>
        </div>
        <div class="form-group">
            <label for="fullname" class="form-label">Full Name (Optional)</label>
            <input type="text" name="fullname" id="fullname" placeholder="Alex Doe" class="form-input">
            <p class="hint">Example: Alex Doe &lt;alex.doe@openmail.com&gt;</p>
        </div>
        <button type="submit" id="add-account-btn">Connect to account.</button>
        <div class="list-accounts-navigation">
            <button onclick={() => { isListingAccount = true; }}>Which accounts have I added?</button>
        </div>
    </div>
</Form>

<style>
    .list-accounts-navigation {
        text-align: center;
        margin-top: 20px;
    }
</style>
