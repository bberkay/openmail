<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";

    interface Props {
        handleCreateFolderForm: (e: Event) => void,
        closeCreateFolderForm: () => void,
        clearInput: (e: Event) => void
    }

    let { handleCreateFolderForm, closeCreateFolderForm, clearInput }: Props = $props();
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
                    <option value="" selected>Select Parent Folder</option>
                    {#each SharedStore.folders[0].result as folder}
                        <option value={folder}>{folder}</option>
                    {/each}
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
