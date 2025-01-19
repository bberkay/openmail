<script lang="ts">
    import { onMount } from "svelte";
    import { mount, unmount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from "$lib/types";
    import { countCharacter, createDomObject, swap, capitalize } from "$lib/utils";
    import Loader from "$lib/components/Elements/Loader.svelte";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";
    import { PostRoutes } from "$lib/services/ApiService";
    import CreateFolderForm from "./Sidebar/CreateFolderForm.svelte";
    import RenameFolderForm from "./Sidebar/RenameFolderForm.svelte";
    import DeleteFolderForm from "./Sidebar/DeleteFolderForm.svelte";
    import MoveFolderForm from "./Sidebar/MoveFolderForm.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

    const mailboxController = new MailboxController();

    let standardFoldersContainer: HTMLDivElement;
    let customFoldersContainer: HTMLDivElement;
    let standardFolders: string[] = [];
    let customFolders: string[] = [];
    interface Props {
        showCompose: () => void
    }

    let { showCompose }: Props = $props();
    interface SidebarMounts {
        mountedCreateFolderForm: Record<string, any> | null,
        mountedRenameFolderForm: Record<string, any> | null
        mountedMoveFolderForm: Record<string, any> | null
        mountedDeleteFolderForm: Record<string, any> | null
    }
    let sidebarMounts: SidebarMounts = {
        mountedCreateFolderForm: null,
        mountedRenameFolderForm: null,
        mountedMoveFolderForm: null,
        mountedDeleteFolderForm: null,
    };

    onMount(() => {
        standardFoldersContainer = document.getElementById("standard-folders") as HTMLDivElement;
        customFoldersContainer = document.getElementById("custom-folders") as HTMLDivElement;
        createStandardFolderMenu();
        createCustomFolderMenu();
    });

    const standardFolderTemplate = `
        <div class="folder" data-tag-name="{tagName}">
            <button class="inline folder-name" style="flex-grow:1;">{folder}</button>
        </div>
    `;

    const customFolderTemplate = `
        <div class="folder" style="padding-left:{tabsize}rem;">
            <button class="inline subfolder-toggle {disabled}" style="opacity:{opacity}">▾</button>
            <button class="inline folder-name" style="flex-grow:1;">{folder}</button>
            <button class="inline hover dropdown-toggle">⋮</button>
        </div>
    `;

    const optionsTemplate = `
        <div class="dropdown">
            <button class="bg-primary" id="create-sub-folder">Add Sub Tag</button>
            <button class="bg-primary" id="rename-folder">Rename</button>
            <button class="bg-primary" id="delete-folder">Delete</button>
            <button class="bg-primary" id="move-folder">Move</button>
        </div>
    `;

    document.body.addEventListener("click", (e: MouseEvent) => {
        const target = e.target as HTMLInputElement;
        const dropdowns = document.querySelectorAll(".dropdown");
        if (!dropdowns.length)
            return;

        if (!target.closest('.dropdown, .dropdown-toggle') || (target.closest('.dropdown') && !target.closest('select'))) {
            dropdowns.forEach(dropdown => dropdown.remove());
        }
    });

    async function handleCreateFolderForm(e: Event): Promise<void> {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const parentFolder = target.querySelector<HTMLSelectElement>(
            'select[name="parent_folder"]',
        )?.value;

        const response = await mailboxController.createFolder(folderName, parentFolder);
        if(!response.success){
            alert(response.message);
        }

        target.reset();
        clearContent();
        createCustomFolderMenu();
    }

    async function handleDeleteFolderForm(e: Event): Promise<void> {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const subfolders = target.querySelector<HTMLInputElement>(
            'input[name="subfolders"]',
        )!.checked;

        const response = await mailboxController.deleteFolder(folderName, subfolders);
        if(!response.success){
            alert(response.message);
        }

        target.reset();
        clearContent();
        createCustomFolderMenu();
    }

    async function handleRenameFolderForm(e: Event): Promise<void> {
        const target = e.target as HTMLFormElement;
        const folderPath = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        let newFolderName = target.querySelector<HTMLSelectElement>(
            'input[name="new_folder_name"]',
        )!.value;

        const response = await mailboxController.renameFolder(folderPath, newFolderName);
        if(!response.success){
            alert(response.message);
        }

        target.reset();
        clearContent();
        createCustomFolderMenu();
    }

    async function handleMoveFolderForm(e: Event): Promise<void> {
        const target = e.target as HTMLFormElement;
        const folderName = target.querySelector<HTMLInputElement>(
            'input[name="folder_name"]',
        )!.value;
        const destinationFolder = target.querySelector<HTMLSelectElement>(
            'select[name="destination_folder"]',
        )!.value;

        const response = await mailboxController.moveFolder(folderName, destinationFolder);
        if(!response.success){
            alert(response.message);
        }

        clearContent();
        createCustomFolderMenu();
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

    async function getEmailsInFolder(e: Event, folderName: string): Promise<void> {
        const response = await mailboxController.searchEmails(folderName);
        if(!response.success) {
            alert(response.message);
        }
    }

    function createStandardFolderMenu() {
        for (const standardFolder of SharedStore.standardFolders[0].result) {
            const [folderTag, folderName] = standardFolder.trim().split(":");
            const folderNode = createDomObject(
                standardFolderTemplate
                    .replace("{tagName}", folderTag)
                    .replace("{folder}", folderName)
            );

            standardFoldersContainer.appendChild(folderNode);

            folderNode.querySelector<HTMLButtonElement>(".folder-name")!.onclick = (e: MouseEvent) => {
                getEmailsInFolder(e, (e.target as HTMLButtonElement).closest(".folder")!.getAttribute("data-tag-name")!);
            }
        }
    }

    function createCustomFolderMenu() {
        SharedStore.customFolders[0].result.sort((a, b) => {
            const aParts = a.split("/");
            const bParts = b.split("/");

            for (let i = 0; i < Math.min(aParts.length, bParts.length); i++) {
                if (aParts[i] < bParts[i]) {
                    return -1;
                } else if (aParts[i] > bParts[i]) {
                    return 1;
                }
            }

            return aParts.length - bParts.length;
        });

        customFoldersContainer.innerHTML = "";

        const addOptionFunctions = (optionsNode: HTMLElement) => {
            optionsNode.querySelector<HTMLButtonElement>("#create-sub-folder")!.onclick = (e: MouseEvent) => {
                showCreateFolder(e);
            };

            optionsNode.querySelector<HTMLButtonElement>("#rename-folder")!.onclick = () => {
                if (sidebarMounts.mountedRenameFolderForm)
                    return;

                clearContent();
                const folderName = getFullFolderPath(optionsNode.closest(".folder")!);
                sidebarMounts.mountedRenameFolderForm = mount(RenameFolderForm, {
                    target: document.getElementById("rename-folder-form-container")!,
                    props: {
                        folderName,
                        handleRenameFolderForm,
                        closeRenameFolderForm: () => {
                            unmount(sidebarMounts.mountedRenameFolderForm!);
                            sidebarMounts.mountedRenameFolderForm = null;
                        }
                    }
                });
            };

            optionsNode.querySelector<HTMLButtonElement>("#delete-folder")!.onclick = () => {
                if (sidebarMounts.mountedDeleteFolderForm)
                    return;

                clearContent();
                const folderName = getFullFolderPath(optionsNode.closest(".folder")!);
                sidebarMounts.mountedDeleteFolderForm = mount(DeleteFolderForm, {
                    target: document.getElementById("delete-folder-form-container")!,
                    props: {
                        folderName,
                        handleDeleteFolderForm,
                        closeDeleteFolderForm: () => {
                            unmount(sidebarMounts.mountedDeleteFolderForm!);
                            sidebarMounts.mountedDeleteFolderForm = null;
                        }
                    }
                });
            };

            optionsNode.querySelector<HTMLButtonElement>("#move-folder")!.onclick = () => {
                if (sidebarMounts.mountedMoveFolderForm)
                    return;

                clearContent();
                const folderName = getFullFolderPath(optionsNode.closest(".folder")!);
                sidebarMounts.mountedMoveFolderForm = mount(MoveFolderForm, {
                    target: document.getElementById("move-folder-form-container")!,
                    props: {
                        folderName,
                        handleMoveFolderForm,
                        closeMoveFolderForm: () => {
                            unmount(sidebarMounts.mountedMoveFolderForm!);
                            sidebarMounts.mountedMoveFolderForm = null;
                        }
                    }
                });
            };
        }

        let i = 0;
        let tabsize = 0;
        let opacity = 0;
        let folderName = "";
        let prevFolderName = "";
        let folderNode: HTMLElement;
        let traversedFolders: string[] = [];
        const tabsizeMultiplier = 0.5;
        const folderLength = customFolders.length;
        while (i < folderLength) {
            opacity = 0;
            tabsize = 0;

            const currentFolder = customFolders[i];
            prevFolderName = folderName;
            folderName = currentFolder;

            if (i < folderLength - 1) {
                const nextFolder = customFolders[i + 1];
                if (nextFolder.startsWith(currentFolder + "/"))
                    opacity = 1;
            }

            if (i > 0) {
                let parentFolder = currentFolder.substring(0, currentFolder.lastIndexOf("/"));
                if (parentFolder) {
                    // if folderName has a slash that does not exists for hierarchy but is a folder name,
                    // then do not add a tabsize for that slash for example:
                    // folders = ['folderthathas/initsname', 'folderthathas/initsname/subfolder']
                    while (!traversedFolders.some(folder => folder === parentFolder)) {
                        parentFolder = parentFolder.substring(0, parentFolder.lastIndexOf("/"));
                        if (!parentFolder)
                            break;
                    }
                    if (parentFolder) {
                        folderName = currentFolder.substring(parentFolder.length + 1);
                        const currentFolderDepth = countCharacter(currentFolder, "/");
                        const previousFolderDepth = countCharacter(prevFolderName, "/")
                        tabsize = (currentFolderDepth - previousFolderDepth) * tabsizeMultiplier;
                    }
                }
            }

            folderNode = createDomObject(
                customFolderTemplate
                    .replace("{opacity}", opacity.toString())
                    .replace("{folder}", folderName)
                    .replace("{tabsize}", tabsize.toString())
                    .replace("{disabled}", opacity === 0 ? "disabled" : ""),
            );

            folderNode.querySelector<HTMLButtonElement>(".folder-name")!.onclick = (e: MouseEvent) => {
                getEmailsInFolder(e, getFullFolderPath((e.target as HTMLButtonElement).closest(".folder")!))
            }

            folderNode.querySelector<HTMLButtonElement>(
                ".subfolder-toggle",
            )!.onclick = (e: MouseEvent) => {
                const toggleButton = e.target as HTMLButtonElement;
                toggleButton.innerText = toggleButton.innerText === "▸" ? "▾" : "▸";
                const isClosing = toggleButton.innerText === "▸";

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
                        if (nextElementTabSize - currentTabsize > tabsizeMultiplier) {
                            const prevSibling = folder.previousElementSibling as HTMLDivElement;
                            const prevSiblingToggle = prevSibling.querySelector(".subfolder-toggle") as HTMLButtonElement;
                            if (!prevSiblingToggle.classList.contains("disabled")) {
                                if (prevSiblingToggle.innerText.includes("▾"))
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

            folderNode.querySelector<HTMLButtonElement>(".dropdown-toggle")!.onclick = (e: MouseEvent) => {
                const toggleButton = e.target as HTMLDivElement;
                const folder = toggleButton.parentElement!;
                const openDropdowns = document.querySelectorAll(".dropdown");

                let isTargetDropdown = false;
                openDropdowns.forEach(dropdown => {
                    isTargetDropdown = dropdown.parentElement == folder;
                    dropdown.remove();
                });

                if (!isTargetDropdown){
                    const optionsNode = createDomObject(optionsTemplate);
                    folder.appendChild(optionsNode);
                    addOptionFunctions(optionsNode);
                }
            };

            customFoldersContainer.appendChild(folderNode);
            traversedFolders.push(currentFolder);
            i += 1;
        }
    }

    function showCreateFolder(e: MouseEvent) {
        if (sidebarMounts.mountedCreateFolderForm)
            return;

        clearContent();
        let parentFolderName = null;
        const parentFolderNode = (e.target as HTMLElement).closest(".folder") as HTMLElement;
        if (parentFolderNode) parentFolderName = getFullFolderPath(parentFolderNode);

        sidebarMounts.mountedCreateFolderForm = mount(CreateFolderForm, {
            target: document.getElementById("create-folder-form-container")!,
            props: {
                parentFolderName,
                handleCreateFolderForm,
                closeCreateFolderForm: () => {
                    unmount(sidebarMounts.mountedCreateFolderForm!);
                    sidebarMounts.mountedCreateFolderForm = null;
                }
            }
        });
    }

    function clearContent() {
        if(sidebarMounts.mountedCreateFolderForm) {
            unmount(sidebarMounts.mountedCreateFolderForm);
            sidebarMounts.mountedCreateFolderForm = null
        }
        if(sidebarMounts.mountedRenameFolderForm) {
            unmount(sidebarMounts.mountedRenameFolderForm);
            sidebarMounts.mountedRenameFolderForm = null
        }
        if(sidebarMounts.mountedMoveFolderForm) {
            unmount(sidebarMounts.mountedMoveFolderForm);
            sidebarMounts.mountedMoveFolderForm = null
        }
        if(sidebarMounts.mountedDeleteFolderForm) {
            unmount(sidebarMounts.mountedDeleteFolderForm);
            sidebarMounts.mountedDeleteFolderForm = null
        }
    }

    async function refreshFolders(e: Event): Promise<void> {
        const response = await mailboxController.refreshFolders();
        if (!response.success) {
            alert(response.message);
        }
    }
</script>

<div class="card">
    <div style="border-bottom:1px solid dimgrey;">
        <h3>Open Mail</h3>
    </div>
    <div>
        <div>
            <button
                class="bg-primary"
                style="width:100%;padding:7x;margin:10px 0;"
                onclick={showCompose}>New Message +</button>
        </div>
        <div style="border-bottom:1px solid dimgrey;">
            <div id="standard-folders"></div>
        </div>
    </div>
    <div style="margin-top:20px;">
        <div style="border-bottom:1px solid dimgrey;display:flex;align-items:center;justify-content:space-between;padding:10px 0;">
            <div>
                <span>Tags</span>
                <button onclick={refreshFolders} class="bg-primary">&#x21bb;</button>
            </div>
            <button onclick={showCreateFolder} class="bg-primary">+</button>
        </div>
        <div id="custom-folders"></div>
    </div>
</div>

<div id="create-folder-form-container"></div>
<div id="rename-folder-form-container"></div>
<div id="delete-folder-form-container"></div>
<div id="move-folder-form-container"></div>
