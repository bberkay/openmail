<script lang="ts">
    import { onMount } from "svelte";
    import type { Response } from "$lib/types";
    import { sharedStore } from "$lib/stores/shared.svelte";

    let addAccountBtn: HTMLButtonElement;
    onMount(() => {
        addAccountBtn = document.getElementById('add-account-btn')! as HTMLButtonElement;
    });

    async function handleAddAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        addAccountBtn.disabled = true;
        addAccountBtn.textContent = 'Adding Account...';
        const response: Response = await fetch(`${sharedStore.server}/add-email-account`, {
            method: 'POST',
            body: new FormData(form)
        }).then(res => res.json());
        if(response.success){
            sharedStore.accounts.push(response.data);
            addAccountBtn.disabled = false;
            addAccountBtn.textContent = 'Add Account';
            form.reset();
        }
    }

    async function getEmailsOfAllAccounts() {
        const response: Response = await fetch(
            `${sharedStore.server}/get-emails/${sharedStore.accounts
                .map((account) => account["email"])
                .join(",")}`,
        ).then((res) => res.json());
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
        const response: Response = await fetch(
            `${sharedStore.server}/get-folders/${sharedStore.accounts
                .map((account) => account["email"])
                .join(",")}`,
        ).then((res) => res.json());
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

<section class="add-email">
    <div class="card">
        <form onsubmit={handleAddAccount}>
            <div class="form-group">
                <label for="fullname">Fullname (Optional)</label>
                <!-- svelte-ignore a11y-autofocus -->
                <input type="text" name="fullname" id="fullname" autocomplete="off" value="Test 42" autofocus>
                <small style="font-style:italic;margn-top:5px;">Enter your fullname to be displayed in the email.</small>
            </div>
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" name="email" id="email" autocomplete="off" value="name@example.com" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" value="123" autocomplete="off" required>
            </div>
            <button type="submit" id="add-account-btn">Add Account</button>
        </form>
    </div>
    {#if sharedStore.accounts && sharedStore.accounts.length > 0}
        <button onclick={continueToInbox}>Continue to Inbox</button>
        <h3>Current Accounts</h3>
        <ul>
            {#each sharedStore.accounts as account}
                <li>{account.fullname} - {account.email}</li>
            {/each}
        </ul>
    {/if}
</section>

<style>
    .add-email{
        width: 100%;
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        & .card{
            width: 300px;
        }
    }
</style>
