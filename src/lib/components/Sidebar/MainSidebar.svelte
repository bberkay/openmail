<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import CreateFolderModal from "$lib/components/Sidebar/CreateFolderModal.svelte";
    import RenameFolderModal from "$lib/components/Sidebar/RenameFolderModal.svelte";
    import DeleteFolderModal from "$lib/components/Sidebar/DeleteFolderModal.svelte";
    import MoveFolderModal from "$lib/components/Sidebar/MoveFolderModal.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import Dropdown from "$lib/components/Elements/Dropdown.svelte";
    import DropdownToggle from "$lib/components/Elements/DropdownToggle.svelte";
    import DropdownItem from "$lib/components/Elements/DropdownItem.svelte";
    import { showModal } from "$lib/components/Elements/Modal.svelte";
    import ToggleButton from "$lib/components/Elements/ToggleButton.svelte";
    import { show as showContent } from "$lib/components/Content.svelte";
    import Compose from "../Compose/Compose.svelte";

    const mailboxController = new MailboxController();
    const TABSIZE_MULTIPLIER = 0.5;

    async function getEmailsInFolder(folderName: string): Promise<void> {
        const response = await mailboxController.searchEmails(folderName);
        if(!response.success) {
            alert(response.message);
        }
    }

    function getFullFolderPath(optionsNode: HTMLElement): string {
        const folder = optionsNode.closest(".folder") as HTMLButtonElement;
        const folderName = folder.querySelector(".folder-name")!.textContent!;

        const parent = optionsNode.previousElementSibling as HTMLButtonElement;
        if(!parent || !parent.classList.contains("folder"))
            return folderName;

        if (parent && parseFloat(parent.style.paddingLeft) < parseFloat(folder.style.paddingLeft)) {
            if (!parent.querySelector(".subfolder-toggle")!.classList.contains("disabled")) {
                const parentFolderName = parent!.querySelector(".folder-name")!.textContent!;
                return getFullFolderPath(parent) + `/${folderName}`
            }
        }

        return folderName;
    }

    function countRealAncestorsOfCustomFolder(path: string): number {
        const parentPath = path.split("/").slice(0, -1).join("/");
        if (!parentPath)
            return 0;
        return (SharedStore.customFolders[0].result.includes(parentPath) ? 1 : 0) + countRealAncestorsOfCustomFolder(parentPath);
    }

    function isCustomFolderAParentFolder(path: string): boolean {
        return SharedStore.customFolders[0].result.filter(customFolder => customFolder == path || customFolder.startsWith(path)).length > 1;
    }

    const showCompose = () => {
        showContent(Compose);
    }

    const showSidebarModal = (e: Event, component: any): void => {
        const target = e.target as HTMLElement;
        const folderNode = target.closest(".folder") as HTMLElement;
        const folderName = folderNode ? getFullFolderPath(folderNode) : null;
        showModal(component, {
            folderName
        });
    }

    const showCreateFolderModal = (e: Event): void => {
        showSidebarModal(e, CreateFolderModal);
    }

    const showRenameFolderModal = (e: Event) => {
        showSidebarModal(e, RenameFolderModal);
    }

    const showDeleteFolderModal = (e: Event) => {
        showSidebarModal(e, DeleteFolderModal);
    }

    const showMoveFolderModal = (e: Event) => {
        showSidebarModal(e, MoveFolderModal);
    }

    const refreshFolders = async (): Promise<void> => {
        const response = await mailboxController.refreshFolders();
        if (!response.success) {
            alert(response.message);
        }
    }

    const toggleSubfolders = (e: Event) => {
        const toggleButton = e.target as HTMLButtonElement;
        if (toggleButton.classList.contains("disabled"))
            return;

        const isClosing = !toggleButton.classList.contains("opened");

        let folder = toggleButton.parentElement!;
        const currentTabsize = parseFloat(folder.style.paddingLeft);
        while (folder.nextElementSibling) {
            folder = folder.nextElementSibling as HTMLDivElement;

            // Determine if the next folder is a subfolder
            // by checking its padding-left/tabsize value.
            const nextElementTabSize = parseFloat(folder.style.paddingLeft);
            if (currentTabsize >= nextElementTabSize)
                break;

            if (!folder.classList.contains("folder"))
                continue;

            if (isClosing) {
                folder.style.display = "none";
            } else {
                // Open the subfolders without changing their current open/close state.
                // If the subfolder was closed, do not open it while opening the parent folder.
                if (nextElementTabSize - currentTabsize > TABSIZE_MULTIPLIER) {
                    const prevSibling = folder.previousElementSibling as HTMLDivElement;
                    const prevSiblingToggle = prevSibling.querySelector(".subfolder-toggle") as HTMLButtonElement;
                    if (!prevSiblingToggle.classList.contains("disabled")) {
                        if (prevSiblingToggle.classList.contains("opened"))
                            folder.style.display = prevSibling.style.display;
                    } else {
                        folder.style.display = prevSibling.style.display;
                    }
                } else {
                    folder.style.display = "flex";
                }
            }
        }
    };
</script>

<div>
    <div>
        <button
            class="bg-primary"
            style="width:100%;padding:7x;margin:10px 0;"
            onclick={showCompose}>New Message +</button>
    </div>
    <div style="border-bottom:1px solid dimgrey;">
        <div id="standard-folders">
            {#each SharedStore.standardFolders[0].result as standardFolder, index}
                {@const [folderTag, folderName] = standardFolder.trim().split(":")}
                <div class="folder">
                    <ActionButton
                        onclick={async (): Promise<void> => { getEmailsInFolder(folderTag) }}
                        class="inline folder-name"
                        style="flex-grow:1;"
                    >
                        {folderName}
                    </ActionButton>
                </div>
            {/each}
        </div>
    </div>
</div>
<div style="margin-top:20px;">
    <div style="border-bottom:1px solid dimgrey;display:flex;align-items:center;justify-content:space-between;padding:10px 0;">
        <div>
            <span>Tags</span>
            <button onclick={refreshFolders} class="bg-primary">&#x21bb;</button>
        </div>
        <button onclick={showCreateFolderModal} class="bg-primary">+</button>
    </div>
    <div id="custom-folders">
        {#each SharedStore.customFolders[0].result as customFolder}
            {@const ancestorCount = countRealAncestorsOfCustomFolder(customFolder)}
            {@const folderName = customFolder.split("/").slice(ancestorCount).join("/")}
            {@const tabsize = ancestorCount * TABSIZE_MULTIPLIER}
            {@const disabled = isCustomFolderAParentFolder(customFolder) ? "" : "disabled"}
            <div class="folder" style="padding-left:{tabsize}rem;">
                <ToggleButton class="inline subfolder-toggle {disabled}" onclick={toggleSubfolders} opened={true} />
                <ActionButton
                    onclick={async (): Promise<void> => { getEmailsInFolder(folderName) }}
                    class="inline folder-name"
                    style="flex-grow:1;"
                >
                    {folderName}
                </ActionButton>
                <Dropdown>
                    <DropdownToggle class="inline">⋮</DropdownToggle>
                    {#snippet content()}
                        <DropdownItem class="bg-primary" onclick={showCreateFolderModal}>Add Sub Tag</DropdownItem>
                        <DropdownItem class="bg-primary" onclick={showRenameFolderModal}>Rename</DropdownItem>
                        <DropdownItem class="bg-primary" onclick={showDeleteFolderModal}>Delete</DropdownItem>
                        <DropdownItem class="bg-primary" onclick={showMoveFolderModal}>Move</DropdownItem>
                    {/snippet}
                </Dropdown>
            </div>
        {/each}
    </div>
</div>

<style>
    .folder :global{
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 0;
        background-color: rgb(36, 36, 36);
        border-bottom: 1px solid rgb(70, 70, 70);
        position: relative;

        & .subfolder-toggle.disabled {
            opacity:0;
            pointer-events: none;
        }

        & .inline{
            text-align: left;
            padding:7px 8px;

            &:hover{
                background-color: rgb(50, 50, 50);
            }

            &:active{
                background-color: rgb(70, 70, 70);
            }
        }

        &:hover{
            background-color: rgb(50, 50, 50);
        }

        &:last-child{
            border-bottom: none;
        }
    }
</style>
