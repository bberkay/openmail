<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";

    interface Props {
        parentFolderName: string | null,
        handleCreateFolderForm: (e: Event) => void,
        closeCreateFolderForm: () => void,
        clearInput: (e: Event) => void
    }

    let { parentFolderName, handleCreateFolderForm, closeCreateFolderForm, clearInput }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        if (parentFolderName) {
            document.getElementById("parent-folder")!.setAttribute("disabled", "true");
        }
    });
</script>

<div class="card absolute">
    <form onsubmit={handleCreateFolderForm}>
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
                    {#if parentFolderName}
                        <option value={parentFolderName} selected>{parentFolderName}</option>
                    {:else}
                        <option value="" selected>Select Parent Folder</option>
                        {#each SharedStore.customFolders[0].result as folder}
                            <option value={folder}>{folder}</option>
                        {/each}
                    {/if}
                </select>
                <button type="button" onclick={clearInput}>X</button>
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Create</button>
            <button type="button" onclick={closeCreateFolderForm}>Cancel</button>
        </div>
    </form>
</div>
