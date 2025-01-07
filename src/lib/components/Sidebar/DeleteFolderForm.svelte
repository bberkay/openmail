<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        handleDeleteFolderForm: (e: Event) => void,
        closeDeleteFolderForm: () => void,
        folderName: string
    }

    let { handleDeleteFolderForm, closeDeleteFolderForm, folderName }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });
</script>

<div class="card absolute">
    <form onsubmit={handleDeleteFolderForm}>
        <div class="form-group">
            <label for="folder-name">Folder Name</label>
            <input
                type="text"
                name="folder_name"
                id="folder-name"
                placeholder="My New Folder"
                value={folderName}
                disabled
                required
            />
        </div>
        <div class="form-group">
            <label for="subfolders">Delete Subfolders</label>
            <input
                type="checkbox"
                name="subfolders"
                id="subfolders"
            />
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Delete</button>
            <button type="button" onclick={closeDeleteFolderForm}>Cancel</button>
        </div>
    </form>
</div>
