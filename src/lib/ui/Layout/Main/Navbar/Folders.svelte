<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import * as Select from "$lib/ui/Components/Select";
    import { show as showMessage } from "$lib/ui/Components/Message";

    let standardFoldersOfAccount = $derived(
        SharedStore.standardFolders.find(
            (acc) =>
                acc.email_address === SharedStore.currentAccount.email_address,
        )!.result,
    );

    let customFoldersOfAccount = $derived(
        SharedStore.customFolders.find(
            (acc) =>
                acc.email_address === SharedStore.currentAccount.email_address,
        )!.result,
    );

    async function setCurrentFolder(selectedFolder: string | Folder) {
        let isSelectedFolderFound = SharedStore.standardFolders.find(
            (task) =>
                task.email_address === SharedStore.currentAccount!.email_address &&
                    task.result.includes(selectedFolder)
        );
        if (!isSelectedFolderFound) {
            isSelectedFolderFound = SharedStore.customFolders.find(
                (task) =>
                    task.email_address === SharedStore.currentAccount!.email_address &&
                        task.result.includes(selectedFolder)
            );
        }
        if (!isSelectedFolderFound) {
            showMessage({content: "Error selected folder could not found!"});
            console.error("Error selected folder could not found!");
            return;
        }

        SharedStore.currentFolder = selectedFolder;
    }

    function createFolder() {

    }

    async function refreshFolders() {
        const response = await MailboxController.getFolders(
            SharedStore.currentAccount,
        );
        if (!response.success) {
            showMessage({ content: "Error while refreshing folders" });
            console.error(response.message);
        }
    }

    function handleOperation(selectedOperation: string) {
        switch (selectedOperation) {
            case "create":
                createFolder();
                break;
            case "refresh":
                refreshFolders();
                break;
            default:
                // if selectedOperation is none of the above, then it
                // must be a folder name.
                setCurrentFolder(selectedOperation);
                break;
        }
    }
</script>

<Select.Root
    onchange={handleOperation}
    value={SharedStore.currentFolder}
    placeholder="Folder"
    enableSearch={true}
>
    {#each standardFoldersOfAccount as standardFolder}
        <Select.Option value={standardFolder}>{standardFolder}</Select.Option>
    {/each}
    <Select.Separator />
    {#each customFoldersOfAccount as customFolder}
        <Select.Option value={customFolder}>{customFolder}</Select.Option>
    {/each}
    <Select.Separator />
    <Select.Option value="create">Create Folder</Select.Option>
    <Select.Option value="refresh">Refresh folders</Select.Option>
</Select.Root>
