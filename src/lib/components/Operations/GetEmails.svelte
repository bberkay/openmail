<script lang="ts">
    import { onMount } from 'svelte';
    import { emails, currentFolder, totalEmailCount, folders } from '$lib/stores';
    import type { Email, OpenMailData } from '$lib/types';
    import SearchMenu from './SearchMenu.svelte';

    let getSearchMenuDict: () => { offset: string; folder: string; search: string };
    let folderSelectOptions: NodeListOf<HTMLFormElement>;
    let isSearchMenuOpen = false;
    let getEmailForm: HTMLFormElement;
    let getEmailButton: HTMLButtonElement;
    onMount(() => {
        getEmailForm = document.getElementById('get-emails-form') as HTMLFormElement;
        getEmailButton = getEmailForm.querySelector('button[type="submit"]') as HTMLButtonElement;

        folderSelectOptions = document.querySelectorAll('#get-emails-form select[name*="folder"]');
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
        });
    });

    function toggleSearchMenu(e: Event){
        isSearchMenuOpen = !isSearchMenuOpen;
        (e.target as HTMLButtonElement).textContent = isSearchMenuOpen ? 'X' : '∨';
    }

    function getFormKeyValues(){
        if(isSearchMenuOpen){
            // TODO: Implement the advanced search menu
            return getSearchMenuDict();
        }else{
            const search = (document.getElementById('search') as HTMLInputElement).value;
            return {
                "offset": "0",
                "folder": (document.getElementById('folder_name') as HTMLSelectElement).value,
                "search": `FROM "${search}" OR TO "${search}" OR SUBJECT "${search}"` // TODO: This may change after the advanced search menu is implemented
            }
        }
    }

    function getFormKeyValuesAsString(){
        const keyValues: {[key: string]: string} = getFormKeyValues();
        return Object.keys(keyValues).map(key => `${key}=${keyValues[key]}`).join('&');
    }

    async function handleGetEmails(event: Event){ 
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        getEmailButton.disabled = true;
        getEmailButton.textContent = 'Loading...';
        // TODO: Add the search functionality
        const response: OpenMailData = await fetch(
            `http://127.0.0.1:8000/get-emails?${getFormKeyValuesAsString()}`
        ).then(res => res.json());
        try{
            if(response.success){
                emails.set(response.data["emails"] as Email[]);
                currentFolder.set(response.data["folder"]);
                totalEmailCount.set(response.data["total"]);
            }
            getEmailButton.disabled = false;
            getEmailButton.textContent = isSearchMenuOpen ? "Search Emails" : "Get Emails";
        }catch{
            console.error(response);
        }
    }
</script>

<section class="get-emails">
    <div class="card">
        <form id="get-emails-form" on:submit={handleGetEmails}>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" autocomplete="off" value="testforprojects42webio@gmail.com" required>
            </div>
            <div class="form-group">
                <label for="folder">Folder</label>
                <select name="folder_name" id="folder_name"></select>
            </div>
            <div class="form-group">
                <label for="search">Search</label>
                <div class="input-group">
                    <input type="text" name="search" id="search" placeholder="Subject or Person">
                    <button type="button" on:click={toggleSearchMenu}>∨</button>
                </div>
                {#if isSearchMenuOpen}
                    <SearchMenu bind:getSearchMenuDict={getSearchMenuDict} />
                {/if}
            </div>
            <button type="submit">{isSearchMenuOpen ? "Search Emails" : "Get Emails"}</button>
        </form>
    </div>
</section>

