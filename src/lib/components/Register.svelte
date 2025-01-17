<script lang="ts">
    import { onMount, mount, unmount } from "svelte";
    import AccountList from "$lib/components/Register/AccountList.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import { Folder } from "$lib/types";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";
    import Form from "$lib/components/Elements/Form.svelte";
    import AddAccountForm from "./Register/AddAccountForm.svelte";
    import EditAccountForm from "./Register/EditAccountForm.svelte";
    import ActionButton from "./Elements/ActionButton.svelte";

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

    async function continueToInbox(): Promise<void> {
        await getFoldersOfAllAccounts();
        await getMailboxesOfAllAccounts();
    }
</script>

{#if SharedStore.failedAccounts.length > 0}
    <h3>Edit Account</h3>
    <EditAccountForm />
{:else}
    <h3>Add Account</h3>
    <AddAccountForm />
{/if}

<AccountList/>

<div>
    <ActionButton classes="bg-primary" id="continue-to-inbox" operation={continueToInbox} inner="Continue To Inbox" />
</div>
