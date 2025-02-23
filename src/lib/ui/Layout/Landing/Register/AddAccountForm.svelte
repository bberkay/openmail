<script lang="ts">
    import { AccountController } from "$lib/controllers/AccountController";
    import Form from "$lib/ui/Elements/Form";

    const accountController = new AccountController();

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
            <label for="email_address">Email Address</label>
            <!-- svelte-ignore a11y_autofocus -->
            <input
                type="email"
                name="email_address"
                id="email_address"
                autocomplete="off"
                value="name@example.com"
                autofocus
                required
            />
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input
                type="password"
                name="password"
                id="password"
                autocomplete="off"
                required
            />
        </div>
        <div class="form-group">
            <label for="fullname">Fullname (Optional)</label>
            <input
                type="text"
                name="fullname"
                id="fullname"
                autocomplete="off"
                value=""
            />
            <small>Enter your fullname to be displayed in the email. (e.g. Alex Doe &lt;alexdoe@domain.com&gt;)</small>
        </div>
        <button type="submit"  id="add-account-btn">Add Account</button>
    </div>
</Form>
