<script lang="ts">
    import { onMount } from "svelte";
    import { mount, unmount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from "$lib/types";
    import { countCharacter, createDomObject } from "$lib/utils";
    import Loader from "$lib/components/Loader.svelte";
    import { ApiService, GetRoutes } from "$lib/services/ApiService";
    import { PostRoutes } from "$lib/services/ApiService";
    import CreateFolderForm from "./Sidebar/CreateFolderForm.svelte";
    import RenameFolderForm from "./Sidebar/RenameFolderForm.svelte";
    import DeleteFolderForm from "./Sidebar/DeleteFolderForm.svelte";
    import MoveFolderForm from "./Sidebar/MoveFolderForm.svelte";

    let folders: HTMLDivElement;
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
        folders = document.getElementById("folders") as HTMLDivElement;
        createFolderMenu();
    });

    document.body.addEventListener("click", (e: MouseEvent) => {
        const target = e.target as HTMLInputElement;
        const dropdowns = document.querySelectorAll(".dropdown");
        if (!dropdowns.length)
            return;

        if (!target.closest('.dropdown, .dropdown-toggle') || (target.closest('.dropdown') && !target.closest('select'))) {
            dropdowns.forEach(dropdown => dropdown.remove());
        }
    });

    async function makeAnApiRequest(e: Event, callback: () => Promise<void>) {
        e.preventDefault();

        const target = e.target as HTMLFormElement;
        const eventButton = target.querySelector(
            'button[type="submit"]',
        ) as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton });

        await callback();

        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
    }

    function handleCreateFolderForm(e: Event) {
        makeAnApiRequest(e, async () => {
            const target = e.target as HTMLFormElement;
            const folderName = target.querySelector<HTMLInputElement>(
                'input[name="folder_name"]',
            )!.value;
            const parentFolder = target.querySelector<HTMLSelectElement>(
                'select[name="parent_folder"]',
            )?.value;

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.CREATE_FOLDER,
                {
                    account: SharedStore.accounts[0].email_address,
                    folder_name: folderName,
                    parent_folder: parentFolder,
                },
            );

            if(response.success){
                SharedStore.folders[0].result.push(parentFolder ? `${parentFolder}/${folderName}` : folderName);
            } else {
                alert(response.message);
            }

            target.reset();
            clearContent();
            createFolderMenu();
        })
    }

    function handleDeleteFolderForm(e: Event) {
        makeAnApiRequest(e, async () => {
            const target = e.target as HTMLFormElement;
            const folderName = target.querySelector<HTMLInputElement>(
                'input[name="folder_name"]',
            )!.value;
            const subfolders = target.querySelector<HTMLInputElement>(
                'input[name="subfolders"]',
            )!.checked;

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.DELETE_FOLDER,
                {
                    account: SharedStore.accounts[0].email_address,
                    folder_name: folderName,
                    subfolders: subfolders
                },
            );

            if(response.success){
                SharedStore.folders[0].result = SharedStore.folders[0].result.filter(e => e !== folderName && !subfolders || !e.includes(folderName));
            } else {
                alert(response.message);
            }

            target.reset();
            clearContent();
            createFolderMenu();
        })
    }

    function handleRenameFolderForm(e: Event) {
        makeAnApiRequest(e, async () => {
            const target = e.target as HTMLFormElement;
            const fullFolderName = target.querySelector<HTMLInputElement>(
                'input[name="folder_name"]',
            )!.value;
            let newFolderName = target.querySelector<HTMLSelectElement>(
                'input[name="new_folder_name"]',
            )!.value;

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.RENAME_FOLDER,
                {
                    account: SharedStore.accounts[0].email_address,
                    folder_name: fullFolderName,
                    new_folder_name: newFolderName,
                },
            );

            if(response.success){
                SharedStore.folders[0].result = SharedStore.folders[0].result.map((currentFolderName) => {
                    return currentFolderName.replace(
                        fullFolderName.includes("/") ? fullFolderName.slice(fullFolderName.lastIndexOf("/") + 1) : fullFolderName,
                        newFolderName
                    )
                });
            } else {
                alert(response.message);
            }

            target.reset();
            clearContent();
            createFolderMenu();
        })
    }

    function handleMoveFolderForm(e: Event) {
        makeAnApiRequest(e, async () => {
            const target = e.target as HTMLFormElement;
            const folderName = target.querySelector<HTMLInputElement>(
                'input[name="folder_name"]',
            )!.value;
            const destinationFolder = target.querySelector<HTMLSelectElement>(
                'select[name="destination_folder"]',
            )!.value;

            const response = await ApiService.post(
                SharedStore.server,
                PostRoutes.MOVE_FOLDER,
                {
                    account: SharedStore.accounts[0].email_address,
                    folder_name: folderName,
                    destination_folder: destinationFolder,
                },
            );

            if(response.success){
                SharedStore.folders[0].result = SharedStore.folders[0].result.filter(e => e !== folderName);

                let newFolderPath = `${destinationFolder}/${folderName}`;
                if (folderName.includes("/")) {
                    const tempLastIndex = folderName.lastIndexOf("/");
                    const parentFolder = folderName.slice(0, tempLastIndex);
                    if (SharedStore.folders[0].result.includes(parentFolder)) {
                        newFolderPath = `${destinationFolder}/${folderName.slice(tempLastIndex+1)}`;
                    }
                }
                SharedStore.folders[0].result.push(newFolderPath);
            } else {
                alert(response.message);
            }

            target.reset();
            clearContent();
            createFolderMenu();
        })
    }

    function clearInput(e: Event) {
        const target = e.target as HTMLButtonElement;
        const inputGroup = target.closest(".input-group")!;

        const targetInputs = inputGroup.querySelectorAll(
            "input",
        ) as NodeListOf<HTMLInputElement>;
        targetInputs.forEach((input: HTMLInputElement) => {
            if (input.type === "number") input.value = "0";
            else input.value = "";
        });

        const targetSelects = inputGroup.querySelectorAll(
            "select",
        ) as NodeListOf<HTMLSelectElement>;
        targetSelects.forEach((select: HTMLSelectElement) => {
            select.selectedIndex = 0;
        });
    }

    function sortFolders() {
      return SharedStore.folders[0].result.sort((a, b) => {
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
    }

    function createFolderMenu() {
        sortFolders();
        folders.innerHTML = "";

        const folderTemplate = `
            <div class="folder" style="padding-left:{tabsize}rem;">
                <button class="inline subfolder-toggle {disabled}" style="opacity:{opacity}">▾</button>
                <button class="inline folder-name" style="flex-grow:1;">{folder}</button>
                <button class="inline hover dropdown-toggle">⋮</button>
            </div>
        `;

        const optionsTemplate = `
            <div class="dropdown">
                <button class="bg-primary" id="rename-folder">Rename</button>
                <button class="bg-primary" id="delete-folder">Delete</button>
                <button class="bg-primary" id="move-folder">Move</button>
            </div>
        `;

        const getFullFolderPath = (optionsNode: HTMLElement): string => {
            const folder = optionsNode.closest(".folder") as HTMLButtonElement;
            const folderName = folder.querySelector(".folder-name")!.textContent!;

            const parent = optionsNode.previousElementSibling as HTMLButtonElement;
            if(!parent.classList.contains("folder"))
                return folderName;

            if (parent && parseFloat(parent.style.paddingLeft) < parseFloat(folder.style.paddingLeft)) {
                if (!parent.querySelector(".subfolder-toggle")!.classList.contains("disabled")) {
                    const parentFolderName = parent!.querySelector(".folder-name")!.textContent!;
                    return getFullFolderPath(parent) + `/${folderName}`
                }
            }

            return folderName;
        }

        const addOptionFunctions = (optionsNode: HTMLElement) => {
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
        const folderLength = SharedStore.folders[0].result.length;
        while (i < folderLength) {
            opacity = 0;
            tabsize = 0;

            const currentFolder = SharedStore.folders[0].result[i];
            prevFolderName = folderName;
            folderName = currentFolder;

            if (i < folderLength - 1) {
                const nextFolder = SharedStore.folders[0].result[i + 1];
                if (nextFolder.startsWith(currentFolder + "/")) opacity = 1;
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
                folderTemplate
                    .replace("{opacity}", opacity.toString())
                    .replace("{folder}", folderName)
                    .replace("{tabsize}", tabsize.toString())
                    .replace("{disabled}", opacity === 0 ? "disabled" : ""),
            )!;

            folderNode.querySelector<HTMLButtonElement>(".folder-name")!.onclick = (e: MouseEvent) => {
                makeAnApiRequest(e, async () => {
                    const target = e.target as HTMLFormElement;
                    const folderName = getFullFolderPath(folderNode);

                    const response = await ApiService.get(
                        SharedStore.server,
                        GetRoutes.GET_MAILBOXES,
                        {
                            pathParams: {
                                accounts: SharedStore.accounts
                                    .map((account) => account.email_address)
                                    .join(",")
                            },
                            queryParams: {
                                folder: folderName
                            }
                        },
                    );

                    if (response.success && response.data) {
                        SharedStore.mailboxes = response.data;
                        SharedStore.currentFolder = response.data[0].result.folder;
                    } else {
                        alert(response.message);
                    }
                })
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
                    if (currentTabsize >= nextElementTabSize) break;

                    if (folder.classList.contains("folder")) {
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

            folders.appendChild(folderNode);
            traversedFolders.push(currentFolder);
            i += 1;
        }
    }

    function showCreateFolder() {
        if (sidebarMounts.mountedCreateFolderForm)
            return;

        clearContent();
        sidebarMounts.mountedCreateFolderForm = mount(CreateFolderForm, {
            target: document.getElementById("create-folder-form-container")!,
            props: {
                handleCreateFolderForm,
                clearInput,
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
                onclick={showCompose}>New Message +</button
            >
        </div>
        <div style="border-bottom:1px solid dimgrey;">
            {#each Object.values(Folder) as folder}
                <div class="folder">
                    <button class="inline" style="flex-grow:1;">{folder}</button>
                </div>
            {/each}
        </div>
    </div>
    <div style="margin-top:20px;">
        <div
            style="border-bottom:1px solid dimgrey;display:flex;align-items:center;justify-content:space-between;padding:10px 0;"
        >
            <span>Folders ▾</span>
            <button onclick={showCreateFolder} class="bg-primary">+</button>
        </div>
        <div id="folders"></div>
    </div>
</div>

<div id="create-folder-form-container"></div>
<div id="rename-folder-form-container"></div>
<div id="delete-folder-form-container"></div>
<div id="move-folder-form-container"></div>
