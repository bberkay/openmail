<script lang="ts">
    import { folders } from '$lib/stores';
    import { onMount } from 'svelte';

    let folderSelectOptions: NodeListOf<HTMLFormElement>;
    onMount(() => {
        folderSelectOptions = document.querySelectorAll('.folder-management-form select[name*="folder"]');
        folders.subscribe(value => {
            if(value.length > 0){
                folderSelectOptions.forEach(select => {
                    value.forEach(folder => {
                        const option = document.createElement('option');
                        option.value = folder;
                        option.innerText = folder;
                        select.appendChild(option);
                    });
                });
            }
        })
    });

    function showFolderManagementForm(event: Event): void {
        const formId = (event.target as HTMLButtonElement).dataset.formTargetId;
        document.querySelector('.folder-management-form.active')!.classList.remove('active');
        document.querySelector(`#${formId}`)!.classList.add('active');
        document.querySelector('.folder-management-buttons .active')!.classList.remove('active');
        (event.target as HTMLButtonElement).classList.add('active');
    }
</script>

<section class="folder-management">
    <div class="folder-management-buttons card">
        <button class="button-text active" data-form-target-id="create-folder-form" on:click={showFolderManagementForm}>Create</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="rename-folder-form" on:click={showFolderManagementForm}>Rename</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="delete-folder-form" on:click={showFolderManagementForm}>Delete</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="move-folder-form" on:click={showFolderManagementForm}>Move</button>
    </div>
    <div class="card">
        <form class = "folder-management-form active" id="create-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder Name</label>
                <input type="text" name="folder_name" id="folder_name" required>
            </div>
            <div class="form-group">
                <label for="parent_folder">Parent Folder</label>
                <select name="parent_folder" id="parent_folder"></select>
            </div>
            <input type="hidden" name="operation" value="create-folder">
            <button type="submit">Create</button>
        </form>
        <form class = "folder-management-form" id="rename-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder Name</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="new_folder_name">New Folder Name</label>
                <input type="text" name="new_folder_name" id="new_folder_name" required>
            </div>
            <input type="hidden" name="operation" value="rename-folder">
            <button type="submit">Rename</button>
        </form>
        <form class = "folder-management-form" id="delete-folder-form">
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <input type="hidden" name="operation" value="delete-folder">
            <button type="submit">Delete</button>
        </form>
        <form class = "folder-management-form" id="move-folder-form">
            <div class="form-group">
                <label for="folder_name">Source Folder</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="destination_folder">Destination Folder</label>
                <select name="destination_folder" id="destination_folder" required></select>
            </div>
            <input type="hidden" name="operation" value="move-folder">
            <button type="submit">Move</button>
        </form>
    </div>
</section>

<style>
    .folder-management-form{
        display: none;

        &.active{
            display: flex;
        }
    }

    .folder-management-buttons{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.25rem;

        & :not(.active){
            opacity: 0.7;
        }

        & .active + span{
            opacity: 1;
        }
    }
</style>