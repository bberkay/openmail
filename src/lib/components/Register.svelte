<script lang="ts">
    import { onMount } from "svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, GetRoutes, PostRoutes, type Response } from "$lib/services/ApiService";

    let addAccountBtn: HTMLButtonElement;
    onMount(() => {
        addAccountBtn = document.getElementById('add-account-btn')! as HTMLButtonElement;
    });

    async function addAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        addAccountBtn.disabled = true;
        addAccountBtn.textContent = 'Adding Account...';

        const formData = new FormData(form);
        const response: Response = await ApiService.post(
            sharedStore.server,
            PostRoutes.ADD_EMAIL_ACCOUNT,
            formData
        );

        if(response.success){
            sharedStore.accounts.push({
                email_address: formData.get('email') as string,
                fullname: formData.get('fullname') as string
            });
        }

        addAccountBtn.disabled = false;
        addAccountBtn.textContent = 'Add Account';
        form.reset();
    }

    async function deleteAccount(event: Event) {
        event.preventDefault();

        const button = event.target as HTMLButtonElement;
        button.textContent = 'Deleting...';
        button.disabled = true;

        const account = button.getAttribute('data-email-address')!
        const response: Response = await ApiService.post(
            sharedStore.server,
            PostRoutes.DELETE_EMAIL_ACCOUNT,
            {
                account: account
            }
        );

        if (response.success) {
            sharedStore.accounts = sharedStore.accounts.filter((item) => item.email_address !== account);
        } else {
            button.disabled = false;
            button.textContent = 'Delete Account';
        }
    }

    async function getEmailsOfAllAccounts() {
        const response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_EMAILS,
            {
                accounts: sharedStore.accounts
                    .map((account) => account.email_address)
                    .join(","),
            }
        );

        if (response.success) {
            sharedStore.inboxes = response.data.map((item: { email: string; data: object }) => ({
                email: item.email,
                ...item.data,
            }));
            sharedStore.selectedFolder = "Inbox";
            sharedStore.currentOffset = response.data["total"] < 10 ? response.data["total"] : 10;
        }
    }

    async function getFoldersOfAllAccounts() {
        const response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                accounts: sharedStore.accounts
                    .map((account) => account.email_address)
                    .join(","),
            }
        )

        if (response.success) {
            sharedStore.folders = response.data.map((item: { email: string; data: any }) => ({
                email: item.email,
                folders: item.data,
            }));
        }
    }

    async function continueToInbox() {
        await getFoldersOfAllAccounts();
        await getEmailsOfAllAccounts();
    }
</script>

<section>
    <form onsubmit={addAccount}>
        <div>
            <label for="email">Email Address</label><br>
            <!-- svelte-ignore a11y_autofocus -->
            <input type="email" name="email" id="email" autocomplete="off" value="name@example.com" autofocus required>
        </div>
        <div>
            <label for="password">Password</label><br>
            <input type="password" name="password" id="password" value="123" autocomplete="off" required>
        </div>
        <div>
            <label for="fullname">Fullname (Optional)</label><br>
            <input type="text" name="fullname" id="fullname" autocomplete="off" value="Test 42"><br>
            <small style="font-style:italic;margin-top:5px;">Enter your fullname to be displayed in the email.</small>
        </div>
        <button type="submit" id="add-account-btn">Add Account</button>
    </form>

    {#if sharedStore.accounts && sharedStore.accounts.length > 0}
        <h3>Current Accounts</h3>
        <ul>
            {#each sharedStore.accounts as account}
                <li>{account.fullname} - &lt;{account.email_address}&gt; <button onclick={deleteAccount} data-email-address={account.email_address}>Delete</button></li>
            {/each}
        </ul>
        <br>
        <button onclick={continueToInbox}>Continue to Inbox</button>
    {/if}
</section>
