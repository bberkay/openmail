<script lang="ts">
    import type { Response } from '$lib/types';
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import { serverUrl, folders, accounts } from '$lib/stores';

    let selectedAccount: string = '';
    let folderSelectOptions: NodeListOf<HTMLFormElement>;
    onMount(() => {
        folderSelectOptions = document.querySelectorAll('.folder-management-form select[name*="folder"]');
        folders.subscribe((value: any) => {
            value = value[0]["folders"];
            if(value.length > 0)
                createFolderOptions(value);
        });
    });

    function selectAccount(event: Event): void {
       selectedAccount = (event.target as HTMLSelectElement).value;
       createFolderOptions(get(folders).filter((folder: any) => folder["email"] === selectedAccount)[0].folders);
    }

    function createFolderOptions(folders: string[]) {
      folderSelectOptions.forEach(select => {
          select.innerHTML = '';
          if(select.name === 'parent_folder'){
              const option = document.createElement('option');
              option.value = '';
              option.innerText = 'Root';
              select.appendChild(option);
          }
          folders.forEach((folder: string) => {
              const option = document.createElement('option');
              option.value = folder;
              option.innerText = folder;
              select.appendChild(option);
          });
      });
    }

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
        await fetch(`${get(serverUrl)}/${operation}`, {
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
		const response: Response = await fetch(`${get(serverUrl)}/get-folders`).then(res => res.json());
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
                <label for="account">Account</label>
                <select name="account" id="account" on:change={selectAccount} required>
                    {#each $accounts as account}
                      <option value={account.email} selected>{account.fullname} &lt;{account.email}&gt;</option>
                    {/each}
                </select>
            </div>
            <button type="submit">Create</button>
        </form>
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
        <form class = "folder-management-form" id="rename-folder" on:submit|preventDefault={handleFormManagementOperation}>
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name" required></select>
            </div>
            <div class="form-group">
                <label for="new_name">New Folder Name</label>
                <input type="text" name="new_name" id="new_name" required>
            </div>
            <button type="submit">Rename</button>
        </form>
        <form class = "folder-management-form" id="delete-folder" on:submit|preventDefault={handleFormManagementOperation}>
            <div class="form-group">
                <label for="folder_name">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <button type="submit">Delete</button>
        </form>
        <form class = "folder-management-form" id="move-folder" on:submit|preventDefault={handleFormManagementOperation}>
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
