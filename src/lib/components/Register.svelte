<script lang="ts">
    import { onMount, createEventDispatcher } from "svelte";
    import type { OpenMailData } from "$lib/types";
    import { get } from "svelte/store";
    import { serverUrl, accounts } from "$lib/stores";

    const dispatch = createEventDispatcher();
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
        const response: OpenMailData = await fetch(`${get(serverUrl)}/add-email-account`, {
            method: 'POST',
            body: new FormData(form)
        }).then(res => res.json());
        if(response.success){
            accounts.update(accounts => [...accounts, response.data]);
            addAccountBtn.disabled = false;
            addAccountBtn.textContent = 'Add Account';
            form.reset();
        }
    }

    function continueToInbox(){
        dispatch('continueToInbox');
    }
</script>

<section class="add-email">
    <div class="card">
        <form on:submit={handleAddAccount}>
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
    {#if $accounts && $accounts.length > 0}
        <button on:click={continueToInbox}>Continue to Inbox</button>
        <h3>Current Accounts</h3>
        <ul>
            {#each $accounts as account}
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
