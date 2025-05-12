<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import { MailboxController } from "$lib/controllers/MailboxController";
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
    import Icon from "$lib/ui/Components/Icon";
    import { isStandardFolder } from "$lib/utils";

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

    const showCreateSubfolder = (parentFolderName: string) => {
        showModal(CreateFolder, { parentFolderName });
    }

    const showRenameFolder = (folderName: string) => {
        showModal(RenameFolder, { folderName });
    }

    const showMoveFolder = (folderName: string) => {
        showModal(MoveFolder, { folderName });
    }

    const showDeleteFolder = (folderName: string) => {
        showModal(DeleteFolder, { folderName })
    }

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
</script>

<Dropdown.Root
    class="dropdown-sm folders"
    disabled={SharedStore.currentAccount === "home"}
>
    <Dropdown.Toggle>
        {isStandardFolder(getCurrentMailbox().folder, Folder.Inbox)
            ? Folder.Inbox
            : getCurrentMailbox().folder}
    </Dropdown.Toggle>
    <Dropdown.Content>
        <Dropdown.Item onclick={showCreateFolder}>
            {local.create_folder[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Item onclick={refreshFolders}>
            {local.refresh_folders[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Separator />
        {#each standardFolders as standardFolder}
            {@const [folderTag, ] = standardFolder.split(":")}
            <Dropdown.Item onclick={() => setCurrentFolder(folderTag)}>
                {folderTag}
            </Dropdown.Item>
        {/each}
        {#if customFolders.length > 0}
            <Dropdown.Separator />
        {/if}
        {#each customFolders as customFolder}
            <Dropdown.Item onclick={() => setCurrentFolder(customFolder)}>
                {customFolder}
                <Dropdown.Root inline={true}>
                    <Dropdown.Toggle class="custom-folder-operations-toggle">
                        <Icon name="ellipsis" />
                    </Dropdown.Toggle>
                    <Dropdown.Content>
                        <Dropdown.Item onclick={() => showCreateSubfolder(customFolder)}>
                            {local.create_subfolder[DEFAULT_LANGUAGE]}
                        </Dropdown.Item>
                        <Dropdown.Item onclick={() => showRenameFolder(customFolder)}>
                            {local.rename_folder[DEFAULT_LANGUAGE]}
                        </Dropdown.Item>
                        <Dropdown.Item onclick={() => showMoveFolder(customFolder)}>
                            {local.move_folder[DEFAULT_LANGUAGE]}
                        </Dropdown.Item>
                        <Dropdown.Item onclick={() => showDeleteFolder(customFolder)}>
                            {local.delete_folder[DEFAULT_LANGUAGE]}
                        </Dropdown.Item>
                    </Dropdown.Content>
                </Dropdown.Root>
            </Dropdown.Item>
        {/each}
    </Dropdown.Content>
</Dropdown.Root>

<style>
    :global {
        nav {
            & .folders {
                & > .dropdown-content {
                    max-height: 80vh!important;
                    overflow-y: scroll;
                    overflow-x: hidden;
                }

                & .dropdown-container.inline .dropdown-toggle {
                    padding: var(--spacing-2xs)!important;

                    & svg {
                        width: var(--font-size-sm);
                        height: var(--font-size-sm);
                    }
                }
            }

            & .custom-folder-operations-toggle {
                color: var(--color-text-secondary);
            }
        }
    }
</style>
