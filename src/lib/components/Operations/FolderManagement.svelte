<script lang="ts">
    import { folders } from '$lib/stores';
    import type { OpenMailData } from '$lib/types';
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

    async function handleFormManagementOperation(e: Event): Promise<void> {
        const submitBtn = (e.target as HTMLFormElement).querySelector('button[type="submit"]')! as HTMLButtonElement;
        const currentText = submitBtn.innerText;
        submitBtn.disabled = true;
        submitBtn.innerText = 'Processing...';
        const operation = (e.target as HTMLFormElement).id;
        await fetch(`http://127.0.0.1:8000/${operation}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(new FormData(e.target as HTMLFormElement)))
        });
        submitBtn.disabled = false;
        submitBtn.innerText = currentText;

        // Update folders
        getFolders();   
    }

    async function getFolders(){
		const response: OpenMailData = await fetch('http://127.0.0.1:8000/get-folders').then(res => res.json());
		folders.set(response.data);
	}
</script>

<section class="folder-management">
    <div class="folder-management-buttons card">
        <button class="button-text active" data-form-target-id="create-folder" on:click={showFolderManagementForm}>Create</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="rename-folder" on:click={showFolderManagementForm}>Rename</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="delete-folder" on:click={showFolderManagementForm}>Delete</button>
        <span>/</span>
        <button class="button-text" data-form-target-id="move-folder" on:click={showFolderManagementForm}>Move</button>
    </div>
    <div class="card">
        <form class = "folder-management-form active" id="create-folder" on:submit|preventDefault={handleFormManagementOperation}>
            <div class="form-group">
                <label for="folder_name">Folder Name</label>
                <input type="text" name="folder_name" id="folder_name" required>
            </div>
            <div class="form-group">
                <label for="parent_folder">Parent Folder</label>
                <select name="parent_folder" id="parent_folder">
                    <option value="">Root</option>
                </select>
            </div>
            <button type="submit">Create</button>
        </form>
        <form class = "folder-management-form" id="rename-folder">
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="new_folder_name">New Folder Name</label>
                <input type="text" name="new_folder_name" id="new_folder_name" required>
            </div>
            <button type="submit">Rename</button>
        </form>
        <form class = "folder-management-form" id="delete-folder">
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <button type="submit">Delete</button>
        </form>
        <form class = "folder-management-form" id="move-folder">
            <div class="form-group">
                <label for="folder_name">Source Folder</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="destination_folder">Destination Folder</label>
                <select name="destination_folder" id="destination_folder" required></select>
            </div>
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