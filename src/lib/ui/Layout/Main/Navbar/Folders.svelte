<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import * as Select from "$lib/ui/Components/Select";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import CreateFolder from "$lib/ui/Layout/Main/Navbar/Folders/CreateFolder.svelte";
    import RenameFolder from "$lib/ui/Layout/Main/Navbar/Folders/RenameFolder.svelte";
    import MoveFolder from "$lib/ui/Layout/Main/Navbar/Folders/MoveFolder.svelte";
    import DeleteFolder from "$lib/ui/Layout/Main/Navbar/Folders/DeleteFolder.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import { show as showMessage } from "$lib/ui/Components/Message";

    const FolderOperation = {
        Create: "create",
        Refresh: "refresh",
    } as const;

    let standardFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.standardFolders[
                  (SharedStore.currentAccount as Account).email_address
              ]
            : [],
    );
    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.customFolders[
                  (SharedStore.currentAccount as Account).email_address
              ]
            : [],
    );

    const setCurrentFolder = async (
        selectedFolder: string | Folder,
    ): Promise<void> => {
        if (SharedStore.currentMailbox.folder !== selectedFolder) {
            if (
                SharedStore.mailboxes[
                    (SharedStore.currentAccount as Account).email_address
                ].folder !== selectedFolder
            ) {
                const response = await MailboxController.getMailboxes(
                    SharedStore.currentAccount as Account,
                    selectedFolder,
                );
                if (!response.success) {
                    showMessage({
                        content: "Error, folder could not fetch.",
                    });
                    console.error(response.message);
                    return;
                }
            }

            SharedStore.currentMailbox =
                SharedStore.mailboxes[
                    (SharedStore.currentAccount as Account).email_address
                ];
        }

        showContent(Mailbox);
    };

    const showCreateFolder = () => {
        showModal(CreateFolder);
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
    value={SharedStore.currentMailbox.folder}
    placeholder="Folder"
    enableSearch={true}
    disabled={SharedStore.currentAccount === "home"}
>
    {#each standardFolders as standardFolder}
        {@const [folderTag, folderName] = standardFolder.split(":")}
        <Select.Option value={folderTag}>{folderName}</Select.Option>
    {/each}
    <Select.Separator />
    <Select.Option value={FolderOperation.Refresh}>
        Refresh folders
    </Select.Option>
    <Select.Option value={FolderOperation.Create}>Create Folder</Select.Option>
    <Select.Separator />
    {#each customFolders as customFolder}
        <Select.Option value={customFolder}>
            <span>{customFolder}</span>
            <Dropdown.Root>
                <Dropdown.Toggle>⋮</Dropdown.Toggle>
                <Dropdown.Content>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(CreateFolder, {
                                parentFolderName: customFolder,
                            })}
                    >
                        Create Subfolder
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(RenameFolder, {
                                folderName: customFolder,
                            })}
                    >
                        Rename Folder
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(MoveFolder, { folderName: customFolder })}
                    >
                        Move Folder
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(DeleteFolder, {
                                folderName: customFolder,
                            })}
                    >
                        Delete Folder
                    </Dropdown.Item>
                </Dropdown.Content>
            </Dropdown.Root>
        </Select.Option>
    {/each}
</Select.Root>
