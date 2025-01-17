<script lang="ts">
    import { onMount, mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import { Folder } from "$lib/types";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";
    import Form from "$lib/components/Elements/Form.svelte";
    import AddAccountForm from "./Register/AddAccountForm.svelte";
    import EditAccountForm from "./Register/EditAccountForm.svelte";

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
            SharedStore.currentFolder = response.data[0].result.folder;
        } else {
            alert(response.message);
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
            const standardFolderList = Object.values(Folder).map(folder => folder.trim().toLowerCase() + ":");
            response.data.forEach((account, i) => {
                // Standard folders
                SharedStore.standardFolders[i] = {
                    email_address: account.email_address,
                    result: []
                };
                standardFolderList.forEach((standardFolder) => {
                    const matchedFolder = account.result.find(
                        currentFolder => currentFolder.trim().toLowerCase().startsWith(standardFolder)
                    );
                    if (matchedFolder)
                        SharedStore.standardFolders[i].result.push(matchedFolder);
                });

                // Custom folders
                SharedStore.customFolders[i] = {
                    email_address: account.email_address,
                    result: []
                };
                SharedStore.customFolders[i].result = account.result.filter((currentFolder) => {
                    return SharedStore.standardFolders[i].result.includes(currentFolder) !== true
                });
            })
        } else {
            alert(response.message);
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

{#if SharedStore.failedAccounts.length > 0}
    <h3>Edit Account</h3>
    <EditAccountForm />
{:else}
    <h3>Add Account</h3>
    <AddAccountForm />
{/if}

{#if SharedStore.accounts && SharedStore.accounts.length > 0}
    <h3>Current Accounts <button onclick={removeAllAccounts}>Remove All</button></h3>
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
