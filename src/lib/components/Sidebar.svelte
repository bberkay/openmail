<script lang="ts">
    import { onMount } from "svelte";
    import { mount, unmount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from "$lib/types";
    import { countCharacter, createDomObject } from "$lib/utils";
    import Loader from "$lib/components/Loader.svelte";
    import { ApiService } from "$lib/services/ApiService";
    import { PostRoutes } from "$lib/services/ApiService";

    let folders: HTMLDivElement;
    let isCreatingFolder = $state(false);
    interface Props {
        showCompose: () => void
    }

    let { showCompose }: Props = $props();
    onMount(() => {
        folders = document.getElementById("folders") as HTMLDivElement;
        createFolderMenu();

        document.body.addEventListener("click", (e: MouseEvent) => {
            const target = e.target as HTMLInputElement;
            const dropdowns = document.querySelectorAll(".dropdown");
            if (!dropdowns.length) return;

            dropdowns.forEach((dropdown) => {
                if (
                    target !== dropdown &&
                    !target.classList.contains("dropdown-toggle")
                )
                    dropdown.remove();
            });
        });
    });

    function toggleCreatingFolder() {
        isCreatingFolder = !isCreatingFolder;
    }

    async function handleCreateFolder(e: Event) {
        e.preventDefault();

        const target = e.target as HTMLFormElement;
        const eventButton = target.querySelector(
            'button[type="submit"]',
        ) as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton });

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

        alert(response.message);
        (e.target as HTMLFormElement).reset();

        if(response.success){
            SharedStore.folders[0].result.push(`${parentFolder}/${folderName}`);
        }

        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
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

    function createFolderMenu() {
        const folderTemplate = `
            <div class="folder" style="padding-left:{tabsize}rem;">
                <button class="inline subfolder-toggle {disabled}" style="opacity:{opacity}">▾</button>
                <button class="inline" style="flex-grow:1;">{folder}</button>
                <button class="inline hover dropdown-toggle">⋮</button>
            </div>
        `;

        const optionsTemplate = `
            <div class="dropdown">
                <button class="bg-primary">Rename</button>
                <button class="bg-primary">Delete</button>
                <select class = "bg-primary" bind:value={folderSelection} onchange={moveEmail}>
                    <option disabled selected>Move to</option>
                    ${SharedStore.folders[0].result.map((folder) => `<option value="${folder}">${folder}</option>`).join("")}
                </select>
            </div>
        `;

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
                const parentFolder = currentFolder.substring(
                    0,
                    currentFolder.lastIndexOf("/"),
                );
                if (parentFolder) {
                    if (
                        traversedFolders.some(
                            (folder) => folder === parentFolder,
                        )
                    ) {
                        folderName = currentFolder.substring(
                            parentFolder.length + 1,
                        );
                        // if prevFolderName has a slash that does not exists for hierarchy but is a folder name,
                        // then do not add a tabsize for that slash for example if the `tabsizeMultiplier` is `0.5`:
                        //
                        // folders = ['myfolderhas/initsname', 'myfolderhas/initsname/subfolder']
                        // oldTabsizeFormula = (currentFolder.split('/').length - 1) * 0.5
                        // and hiearchy should be like this:
                        // myfolderhas/initsname
                        //  subfolder[0.5rem tabsize]
                        // but instead it is:
                        // myfolderhas/initsname
                        //    subfolder[1rem tabsize]
                        //
                        // because parent folder has a slash does not indicate a hierarchy but rather a folder name.
                        // so we should not add any tabsize for that slash and for that we need to store `prevFolderName`
                        // in this case it will be `myfolderhas/initsname` and check if it has a slash or not.
                        //
                        // New Formula with `prevFolderName`:
                        // currentFolder = 'myfolderhas/initsname/subfolder'
                        // prevFolderName = 'myfolderhas/initsname'
                        // tabsize = (currentFolder.split('/').length - 1 - countCharacter(prevFolderName, '/')) * 0.5
                        // means `tabsize = (2 - 1 - 1) * 0.5 = 0.5` as it should be.
                        // and new hierarchy should be like this:
                        // myfolderhas/initsname
                        //  subfolder[0.5rem tabsize]
                        tabsize =
                            (currentFolder.split("/").length -
                                1 -
                                countCharacter(prevFolderName, "/")) *
                            tabsizeMultiplier;
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

            (
                folderNode.querySelector(
                    ".subfolder-toggle",
                ) as HTMLButtonElement
            ).onclick = (e: MouseEvent) => {
                const toggleButton = e.target as HTMLButtonElement;
                toggleButton.innerText =
                    toggleButton.innerText === "▸" ? "▾" : "▸";
                const isClosing = toggleButton.innerText === "▸";

                let folder = toggleButton.parentElement!;
                const currentTabsize = parseFloat(folder.style.paddingLeft);
                while (folder.nextElementSibling) {
                    folder = folder.nextElementSibling as HTMLDivElement;

                    // Determine if the next folder is a subfolder
                    // by checking its padding-left/tabsize value.
                    // for example if the `tabsizeMultiplier` is `0.5`:
                    //
                    // parentfolder[0rem tabsize]
                    //  subfolder[0.5rem tabsize] <- current tabsize
                    //     subsubfolder[1rem tabsize] <- will be a subfolder because `currentTabsize(0.5) < nextElementTabSize(1)`
                    // nextfolder[0rem tabsize] <- will not be a subfolder because `currentTabsize(0.5) >= nextElementTabSize(0)`
                    const nextElementTabSize = parseFloat(
                        folder.style.paddingLeft,
                    );
                    if (currentTabsize >= nextElementTabSize) break;

                    if (folder.classList.contains("folder")) {
                        if (isClosing) {
                            folder.style.display = "none";
                        } else {
                            // While opening the subfolders check their current open/close state.
                            // Do not open subfolder if the parent folder is closed. For example:
                            //
                            // ▾ parentfolder <- this one closed after "subfolder"
                            //  ▾ subfolder <- this one closed before "parentfolder"
                            //     subsubfolder1
                            //     subsubfolder2
                            //
                            // After close:
                            // ▸ parentfolder
                            //
                            // After open the "parentfolder" the hierarchy should be like this:
                            // ▾ parentfolder
                            //  ▸ subfolder
                            //
                            // Not like this:
                            // ▾ parentfolder
                            //  ▾ subfolder
                            //     subsubfolder1
                            //     subsubfolder2
                            //
                            if (
                                nextElementTabSize - currentTabsize >
                                tabsizeMultiplier
                            ) {
                                const prevSibling =
                                    folder.previousElementSibling as HTMLDivElement;
                                const prevSiblingToggle =
                                    prevSibling.querySelector(
                                        ".subfolder-toggle",
                                    ) as HTMLButtonElement;
                                if (
                                    !prevSiblingToggle.classList.contains(
                                        "disabled",
                                    )
                                ) {
                                    if (
                                        prevSiblingToggle.innerText.includes(
                                            "▾",
                                        )
                                    )
                                        folder.style.display =
                                            prevSibling.style.display;
                                } else {
                                    folder.style.display =
                                        prevSibling.style.display;
                                }
                            } else {
                                folder.style.display = "flex";
                            }
                        }
                    }
                }
            };

            (
                folderNode.querySelector(
                    ".dropdown-toggle",
                ) as HTMLButtonElement
            ).onclick = (e: MouseEvent) => {
                const toggleButton = e.target as HTMLDivElement;
                const folder = toggleButton.parentElement!;
                if (folder.querySelector(".dropdown")) {
                    folder.removeChild(folder.querySelector(".dropdown")!);
                } else {
                    const optionsNode = createDomObject(optionsTemplate);
                    folder.appendChild(optionsNode!);
                }
            };

            folders.appendChild(folderNode);
            traversedFolders.push(currentFolder);
            i += 1;
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
                    <button class="inline" style="flex-grow:1;">{folder}</button
                    >
                </div>
            {/each}
        </div>
    </div>
    <div style="margin-top:20px;">
        <div
            style="border-bottom:1px solid dimgrey;display:flex;align-items:center;justify-content:space-between;padding:10px 0;"
        >
            <span>Folders ▾</span>
            <button onclick={() => { isCreatingFolder = true; }} class="bg-primary">+</button>
        </div>
        <div id="folders"></div>
    </div>
</div>

{#if isCreatingFolder}
    <div class="card absolute">
        <form onsubmit={handleCreateFolder}>
            <div class="form-group">
                <label for="folder-name">Folder Name</label>
                <input
                    type="text"
                    name="folder_name"
                    id="folder-name"
                    placeholder="My New Folder"
                    required
                />
            </div>
            <div class="form-group">
                <label for="parent-folder">Parent Folder</label>
                <div class="input-group">
                    <select name="parent_folder" id="parent-folder">
                        <option value="" selected>Select Parent Folder</option>
                        {#each SharedStore.folders[0].result as folder}
                            <option value={folder}>{folder}</option>
                        {/each}
                    </select>
                    <button type="button" onclick={clearInput}>X</button>
                </div>
            </div>
            <button type="submit" class="bg-primary">Create</button>
            <button type="button" onclick={toggleCreatingFolder}>Close</button>
        </form>
    </div>
{/if}

<style>
    .card.absolute {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
</style>
