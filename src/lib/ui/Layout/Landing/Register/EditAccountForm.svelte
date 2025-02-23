<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { type Account } from "$lib/types";
    import Form from "$lib/ui/Elements/Form";

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

    const cancelEdit = () => {
        isEditingAccount = null;
    };
</script>

{#if isEditingAccount}
    <Form onsubmit={editAccount}>
        <div>
            <div>
                <label for="email_address">Email Address</label><br />
                <input
                    type="email"
                    name="email_address"
                    id="email_address"
                    autocomplete="off"
                    placeholder="someone@domain.xyz"
                    value={isEditingAccount.email_address}
                    readonly
                    required
                />
            </div>
            <div>
                <label for="password">Password</label><br />
                <!-- svelte-ignore a11y_autofocus -->
                <input
                    type="password"
                    name="password"
                    id="password"
                    autocomplete="off"
                    autofocus
                    required
                />
            </div>
            <div>
                <label for="fullname">Fullname (Optional)</label><br />
                <input
                    type="text"
                    name="fullname"
                    id="fullname"
                    autocomplete="off"
                    placeholder="Fullname"
                    value={isEditingAccount.fullname}
                /><br />
                <small style="font-style:italic;margin-top:5px;"
                    >Enter your fullname to be displayed in the email.</small
                >
            </div>
            <button type="submit" id="edit-account-btn">Edit Account</button>
            <button type="button" class="inline" onclick={cancelEdit}>Cancel</button>
        </div>
    </Form>
{/if}
