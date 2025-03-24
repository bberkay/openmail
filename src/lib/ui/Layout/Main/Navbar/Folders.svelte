<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import * as Select from "$lib/ui/Components/Select";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import CreateFolder from "$lib/ui/Layout/Main/Navbar/Folders/CreateFolder.svelte";
    import RenameFolder from "$lib/ui/Layout/Main/Navbar/Folders/RenameFolder.svelte";
    import MoveFolder from "$lib/ui/Layout/Main/Navbar/Folders/MoveFolder.svelte";
    import DeleteFolder from "$lib/ui/Layout/Main/Navbar/Folders/DeleteFolder.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";

    const FolderOperation = {
        Create: "create",
        Refresh: "refresh",
    } as const;

    let standardFoldersOfAccount = $derived(
        SharedStore.standardFolders.find(
            (acc) =>
                acc.email_address ===
                (SharedStore.currentAccount as Account).email_address,
        )!.result,
    );

    let customFoldersOfAccount = $derived(
        SharedStore.customFolders.find(
            (acc) =>
                acc.email_address ===
                (SharedStore.currentAccount as Account).email_address,
        )!.result,
    );

    const setCurrentFolder = async (
        selectedFolder: string | Folder,
    ): Promise<void> => {
        let isSelectedFolderFound = SharedStore.standardFolders.find(
            (task) =>
                task.email_address ===
                    (SharedStore.currentAccount as Account).email_address &&
                task.result.includes(selectedFolder),
        );
        if (!isSelectedFolderFound) {
            isSelectedFolderFound = SharedStore.customFolders.find(
                (task) =>
                    task.email_address ===
                        (SharedStore.currentAccount as Account).email_address &&
                    task.result.includes(selectedFolder),
            );
        }
        if (!isSelectedFolderFound) {
            showMessage({ content: "Error selected folder could not found!" });
            console.error("Error selected folder could not found!");
            return;
        }

        SharedStore.currentFolder = selectedFolder;
    };

    const showCreateFolder = () => {
        showModal(CreateFolder);
    };

    const showCreateSubfolder = (parentFolderName: string) => {
        showModal(CreateFolder, { parentFolderName });
    };

    const showRenameFolder = (folderName: string) => {
        showModal(RenameFolder, { folderName });
    };

    const showMoveFolder = (folderName: string) => {
        showModal(MoveFolder, { folderName });
    };

    const showDeleteFolder = (folderName: string) => {
        showModal(DeleteFolder, { folderName });
    };

    const refreshFolders = async () => {
        const response = await MailboxController.getFolders(
            SharedStore.currentAccount as Account,
        );
        if (!response.success) {
            showMessage({ content: "Error while refreshing folders" });
            console.error(response.message);
        }
    };

    const handleOperation = (selectedOperation: string) => {
        switch (selectedOperation) {
            case FolderOperation.Create:
                showCreateFolder();
                break;
            case FolderOperation.Refresh:
                refreshFolders();
                break;
            default:
                // if selectedOperation is none of the above, then it
                // must be a folder name.
                setCurrentFolder(selectedOperation);
                break;
        }
    };
</script>

<Select.Root
    onchange={handleOperation}
    value={SharedStore.currentFolder}
    placeholder="Folder"
    enableSearch={true}
    disabled={SharedStore.currentAccount === "home"}
>
    {#each standardFoldersOfAccount as standardFolder}
        {@const [folderTag, folderName] = standardFolder.split(":")}
        <Select.Option value={folderTag}>{folderName}</Select.Option>
    {/each}
    <Select.Separator />
    {#each customFoldersOfAccount as customFolder}
        <Select.Option value={customFolder}>
            <span>{customFolder}</span>
            <Dropdown.Root>
                <Dropdown.Toggle>⋮</Dropdown.Toggle>
                <Dropdown.Content>
                    <Dropdown.Item
                        onclick={() => showCreateSubfolder(customFolder)}
                    >
                        Create Subfolder
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() => showRenameFolder(customFolder)}
                    >
                        Rename Folder
                    </Dropdown.Item>
                    <Dropdown.Item onclick={() => showMoveFolder(customFolder)}>
                        Move Folder
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() => showDeleteFolder(customFolder)}
                    >
                        Delete Folder
                    </Dropdown.Item>
                </Dropdown.Content>
            </Dropdown.Root>
        </Select.Option>
    {/each}
    <Select.Separator />
    <Select.Option value={FolderOperation.Create}>Create Folder</Select.Option>
    <Select.Option value={FolderOperation.Refresh}>
        Refresh folders
    </Select.Option>
</Select.Root>
