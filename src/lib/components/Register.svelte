<script lang="ts">
    import { onMount, mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import { ApiService, GetRoutes, PostRoutes, type Response } from "$lib/services/ApiService";

    let currentEditingAccount: Account | null = $state(sharedStore.failedAccounts ? sharedStore.failedAccounts[0] : null);

    async function addAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        const addAccountBtn = document.getElementById('add-account-btn')! as HTMLButtonElement;
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
                email_address: formData.get('email_address') as string,
                fullname: formData.get('fullname') as string
            });
        } else {
            // Show alert
        }

        addAccountBtn.disabled = false;
        addAccountBtn.textContent = 'Add Account';
        form.reset();
    }

    async function editAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement) || !currentEditingAccount)
            return;

        const editAccountBtn = document.getElementById('edit-account-btn')! as HTMLButtonElement;
        editAccountBtn.disabled = true;
        editAccountBtn.textContent = 'Editing Account...';

        const formData = new FormData(form);
        const response: Response = await ApiService.post(
            sharedStore.server,
            PostRoutes.EDIT_EMAIL_ACCOUNT,
            formData
        );

        if(response.success){
            sharedStore.accounts.push({
                email_address: currentEditingAccount.email_address,
                fullname: formData.get('fullname') as string
            });

            sharedStore.failedAccounts = sharedStore.failedAccounts.filter(
                (item) => item.email_address !== currentEditingAccount!.email_address
            );
            if(sharedStore.failedAccounts.length > 0){
                currentEditingAccount = sharedStore.failedAccounts[0];
            }
        } else {
            if (sharedStore.failedAccounts.find((item) => item.email_address !== currentEditingAccount!.email_address)) {
                sharedStore.failedAccounts.push({
                    email_address: currentEditingAccount.email_address,
                    fullname: formData.get('fullname') as string
                });
            }
        }

        editAccountBtn.disabled = false;
        editAccountBtn.textContent = 'Edit Account';
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
                pathParams: {
                    accounts: sharedStore.accounts
                        .map((account) => account.email_address)
                        .join(",")
                }
            }
        );

        if (response.success) {
            console.log("emails response", response);
            sharedStore.mailboxes = response.data;
            sharedStore.selectedFolder = "Inbox";
            sharedStore.currentOffset = 10;
        }
    }

    async function getFoldersOfAllAccounts() {
        const response: Response = await ApiService.get(
            sharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: sharedStore.accounts
                        .map((account) => account.email_address)
                        .join(","),
                }
            }
        )

        if (response.success) {
            sharedStore.folders = response.data;
        }
    }

    async function continueToInbox(event: Event) {
        event.preventDefault();

        const continueToInboxBtn = event.target as HTMLButtonElement;

        continueToInboxBtn.disabled = true;
        continueToInboxBtn.innerText = '';
        const loader = mount(Loader, {
            target: continueToInboxBtn,
        });

        await getFoldersOfAllAccounts();
        await getEmailsOfAllAccounts();

        continueToInboxBtn.disabled = false;
        unmount(loader);
        continueToInboxBtn.innerHTML = 'Continue to Inbox';
    }
</script>

<section>
    {#if currentEditingAccount}
        <h3>Updating accounts</h3>
        <small>There were {sharedStore.failedAccounts.length} accounts that failed to connect.</small>
        <ul>
            {#each sharedStore.failedAccounts as account}
                <li>
                    <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                    <button style="margin-right: 5px;" onclick={() => { currentEditingAccount = account }}>Edit</button>
                    <button onclick={deleteAccount} data-email-address={account.email_address}>Remove</button>
                </li>
            {/each}
        </ul>
        <hr>
        <h3>Edit Account</h3>
        <form onsubmit={editAccount}>
            <div>
                <label for="email_address">Email Address</label><br>
                <input type="email" name="email_address" id="email_address" autocomplete="off" value="{currentEditingAccount.email_address}" readonly required>
            </div>
            <div>
                <label for="password">Password</label><br>
                <!-- svelte-ignore a11y_autofocus -->
                <input type="password" name="password" id="password" autocomplete="off" autofocus required>
            </div>
            <div>
                <label for="fullname">Fullname (Optional)</label><br>
                <input type="text" name="fullname" id="fullname" autocomplete="off" value="{currentEditingAccount.fullname}"><br>
                <small style="font-style:italic;margin-top:5px;">Enter your fullname to be displayed in the email.</small>
            </div>
            <button type="submit" id="edit-account-btn">Edit Account</button>
            <button onclick={deleteAccount} data-email-address={currentEditingAccount.email_address}>Remove</button>
        </form>
    {:else}
        <h3>Add Account</h3>
        <form onsubmit={addAccount}>
            <div>
                <label for="email_address">Email Address</label><br>
                <!-- svelte-ignore a11y_autofocus -->
                <input type="email" name="email_address" id="email_address" autocomplete="off" value="name@example.com" autofocus required>
            </div>
            <div>
                <label for="password">Password</label><br>
                <input type="password" name="password" id="password" autocomplete="off" required>
            </div>
            <div>
                <label for="fullname">Fullname (Optional)</label><br>
                <input type="text" name="fullname" id="fullname" autocomplete="off" value="Test 42"><br>
                <small style="font-style:italic;margin-top:5px;">Enter your fullname to be displayed in the email.</small>
            </div>
            <button type="submit" id="add-account-btn">Add Account</button>
        </form>
    {/if}

    {#if sharedStore.accounts && sharedStore.accounts.length > 0}
        <h3>Current Accounts</h3>
        <ul>
            {#each sharedStore.accounts as account}
                <li>
                    <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                    <button style="margin-right: 5px;" onclick={() => { currentEditingAccount = account }}>Edit</button>
                    <button onclick={deleteAccount} data-email-address={account.email_address}>Remove</button>
                </li>
            {/each}
        </ul>
        <button class ="bg-primary" id="continue-to-inbox" onclick={continueToInbox}>Continue to Inbox</button>
    {/if}
</section>
