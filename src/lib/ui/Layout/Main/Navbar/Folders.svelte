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
    import Mailbox, {
        getCurrentMailbox,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    const FolderOperation = {
        Create: "create",
        Refresh: "refresh",
    } as const;

    let standardFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].standard
            : [Folder.Inbox],
    );
    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].custom
            : [],
    );

    const setCurrentFolder = async (
        selectedFolder: string | Folder,
    ): Promise<void> => {
        if (getCurrentMailbox().folder !== selectedFolder) {
            const response = await MailboxController.getMailbox(
                SharedStore.currentAccount as Account,
                selectedFolder,
            );
            if (!response.success) {
                showMessage({
                    title: local.error_get_mailbox[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
                return;
            }
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
            showMessage({
                title: local.error_refresh_folders[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        showToast({ content: "folders are refreshred" });
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
    class="folders"
    onchange={handleOperation}
    value={getCurrentMailbox().folder}
    enableSearch={true}
    searchAlgorithm={(option: HTMLElement) => option.hasAttribute("data-option-searchable")}
    disabled={SharedStore.currentAccount === "home"}
    disableClearButton={true}
>
    {#each standardFolders as standardFolder}
        {@const [folderTag, folderName] = standardFolder.split(":")}
        <Select.Option
            value={folderTag}
            content={folderName || folderTag}
            data-option-searchable
        />
    {/each}
    <Select.Separator />
    <Select.Option
        value={FolderOperation.Refresh}
        content={local.refresh_folders[DEFAULT_LANGUAGE]}
    />
    <Select.Option
        value={FolderOperation.Create}
        content={local.create_folder[DEFAULT_LANGUAGE]}
    />
    {#if customFolders.length > 0}
        <Select.Separator />
    {/if}
    {#each customFolders as customFolder}
        <Select.Option
            value={customFolder}
            content={customFolder}
            data-option-searchable
        />
        <!-- FIXME -->
        <!--<Select.Option value={customFolder}>
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
                        {local.create_subfolder[DEFAULT_LANGUAGE]}
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(RenameFolder, {
                                folderName: customFolder,
                            })}
                    >
                        {local.rename_folder[DEFAULT_LANGUAGE]}
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(MoveFolder, {
                                folderName: customFolder,
                            })}
                    >
                        {local.move_folder[DEFAULT_LANGUAGE]}
                    </Dropdown.Item>
                    <Dropdown.Item
                        onclick={() =>
                            showModal(DeleteFolder, {
                                folderName: customFolder,
                            })}
                    >
                        {local.delete_folder[DEFAULT_LANGUAGE]}
                    </Dropdown.Item>
                </Dropdown.Content>
            </Dropdown.Root>
        </Select.Option>-->
    {/each}
</Select.Root>
