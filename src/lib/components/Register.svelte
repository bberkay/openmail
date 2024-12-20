<script lang="ts">
    import { onMount, mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import { ApiService, GetRoutes, PostRoutes } from "$lib/services/ApiService";
    import { RSAEncryptor } from "$lib/services/RSAEncryptor";

    let currentEditingAccount: Account | null = $state(
        SharedStore.failedAccounts
            ? SharedStore.failedAccounts[0]
            : null
    );

    async function addAccount(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        const addAccountBtn = document.getElementById('add-account-btn')! as HTMLButtonElement;
        addAccountBtn.disabled = true;
        addAccountBtn.textContent = 'Adding Account...';

        const formData = new FormData(form);
        const encryptor = new RSAEncryptor();
        const encryptedPassword = await encryptor.encryptPassword(formData.get("password") as string);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.ADD_ACCOUNT,
            {
                email_address: formData.get('email_address') as string,
                fullname: formData.get('fullname') as string,
                encrypted_password: encryptedPassword
            }
        );

        if(response.success){
            SharedStore.accounts.push({
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
        const encryptor = new RSAEncryptor();
        const encryptedPassword = await encryptor.encryptPassword(formData.get("password") as string);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.EDIT_ACCOUNT,
            {
                email_address: formData.get('email_address') as string,
                fullname: formData.get('fullname') as string,
                encrypted_password: encryptedPassword
            }
        );

        if(response.success){
            SharedStore.accounts.push({
                email_address: currentEditingAccount.email_address,
                fullname: formData.get('fullname') as string
            });

            SharedStore.failedAccounts = SharedStore.failedAccounts.filter(
                (item) => item.email_address !== currentEditingAccount!.email_address
            );

            if(SharedStore.failedAccounts.length > 0){
                currentEditingAccount = SharedStore.failedAccounts[0];
            }
        } else {
            if (SharedStore.failedAccounts.find((item) => item.email_address !== currentEditingAccount!.email_address)) {
                SharedStore.failedAccounts.push({
                    email_address: currentEditingAccount.email_address,
                    fullname: formData.get('fullname') as string
                });
            }
        }

        editAccountBtn.disabled = false;
        editAccountBtn.textContent = 'Edit Account';
        form.reset();
    }

    async function removeAccount(event: Event) {
        event.preventDefault();

        const button = event.target as HTMLButtonElement;
        button.textContent = 'Deleting...';
        button.disabled = true;

        const account = button.getAttribute('data-email-address')!
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNT,
            {
                account: account
            }
        );

        if (response.success) {
            SharedStore.accounts = SharedStore.accounts.filter((item) => item.email_address !== account);
        } else {
            button.disabled = false;
            button.textContent = 'Delete Account';
        }
    }

    async function getMailboxesOfAllAccounts() {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.accounts
                        .map((account) => account.email_address)
                        .join(",")
                }
            }
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
            SharedStore.selectedFolder = response.data[0].result.folder;
        }
    }

    async function getFoldersOfAllAccounts() {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: SharedStore.accounts
                        .map((account) => account.email_address)
                        .join(","),
                }
            }
        );

        if (response.success && response.data) {
            SharedStore.folders = response.data;
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
        await getMailboxesOfAllAccounts();

        continueToInboxBtn.disabled = false;
        unmount(loader);
        continueToInboxBtn.innerHTML = 'Continue to Inbox';
    }
</script>

<section>
    {#if currentEditingAccount}
        <h3>Updating accounts</h3>
        <small>There were {SharedStore.failedAccounts.length} accounts that failed to connect.</small>
        <ul>
            {#each SharedStore.failedAccounts as account}
                <li>
                    <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                    <button style="margin-right: 5px;" onclick={() => { currentEditingAccount = account }}>Edit</button>
                    <button onclick={removeAccount} data-email-address={account.email_address}>Remove</button>
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
            <button onclick={removeAccount} data-email-address={currentEditingAccount.email_address}>Remove</button>
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

    {#if SharedStore.accounts && SharedStore.accounts.length > 0}
        <h3>Current Accounts</h3>
        <ul>
            {#each SharedStore.accounts as account}
                <li>
                    <span style="margin-right: 5px;">{account.fullname} &lt;{account.email_address}&gt;</span>
                    <button style="margin-right: 5px;" onclick={() => { currentEditingAccount = account }}>Edit</button>
                    <button onclick={removeAccount} data-email-address={account.email_address}>Remove</button>
                </li>
            {/each}
        </ul>
        <button class ="bg-primary" id="continue-to-inbox" onclick={continueToInbox}>Continue to Inbox</button>
    {/if}
</section>
