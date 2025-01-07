<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";

    interface Props {
        handleMoveFolderForm: (e: Event) => void,
        closeMoveFolderForm: () => void,
        folderName: string
    }

    let { handleMoveFolderForm, closeMoveFolderForm, folderName }: Props = $props();
    let selectedFolder: string = $state(folderName);
</script>

<div class="card absolute">
    <form onsubmit={handleMoveFolderForm}>
        <div class="form-group">
            <label for="folder-name">Select Folder</label>
            <div class="input-group">
                <select name="folder_name" id="folder-name" bind:value={selectedFolder}>
                    <option value="" selected>Select Folder</option>
                    {#each SharedStore.folders[0].result as folder}
                        <option value={folder}>{folder}</option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="form-group">
            <label for="destination-folder">Destination Folder</label>
            <div class="input-group">
                <select name="destination_folder" id="destination-folder">
                    <option value="" selected>Select Destination Folder</option>
                    {#each SharedStore.folders[0].result.filter((folder) => folder !== selectedFolder) as folder}
                        <option value={folder}>{folder}</option>
                    {/each}
                </select>
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Move</button>
            <button type="button" onclick={closeMoveFolderForm}>Cancel</button>
        </div>
    </form>
</div>
