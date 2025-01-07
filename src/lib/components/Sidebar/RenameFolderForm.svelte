<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        handleRenameFolderForm: (e: Event) => void,
        closeRenameFolderForm: () => void,
        folderName: string
    }

    let { handleRenameFolderForm, closeRenameFolderForm, folderName }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });
</script>

<div class="card absolute">
    <form onsubmit={handleRenameFolderForm} id="rename-folder-form">
        <div class="form-group">
            <label for="folder-name">Folder Name</label>
            <input
                type="text"
                name="folder_name"
                id="folder-name"
                value={folderName}
                disabled
                required
            />
        </div>
        <div class="form-group">
            <label for="new-folder-name">New Folder Name</label>
            <div class="input-group">
                <input
                    type="text"
                    name="new_folder_name"
                    id="new-folder-name"
                    placeholder="New Folder Name"
                    required
                />
            </div>
        </div>
        <div class="display:flex;justify-content:space-between:align-items:center;">
            <button type="submit" class="bg-primary">Rename</button>
            <button type="button" onclick={closeRenameFolderForm}>Cancel</button>
        </div>
    </form>
</div>
