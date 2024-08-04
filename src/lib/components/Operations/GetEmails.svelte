<script lang="ts">
    import { onMount } from 'svelte';
    import { emails, currentFolder, totalEmailCount, folders, currentOffset, serverUrl, accounts } from '$lib/stores';
    import type { Email, OpenMailData, SearchCriteria } from '$lib/types';
    import SearchMenu from './SearchMenu.svelte';
    import { get } from 'svelte/store';

    let getSearchMenuValues: () => SearchCriteria | "";
    let isSearchMenuOpen = false;
    let getEmailForm: HTMLFormElement;
    let getEmailButton: HTMLButtonElement;
    onMount(() => {
        getEmailForm = document.getElementById('get-emails-form') as HTMLFormElement;
        getEmailButton = getEmailForm.querySelector('button[type="submit"]') as HTMLButtonElement;
    });

    function toggleSearchMenu(e: Event){
        isSearchMenuOpen = !isSearchMenuOpen;
        (e.target as HTMLButtonElement).textContent = isSearchMenuOpen ? 'X' : '∨';
    }

    function getFormKeyValuesAsString(){
        const folder = encodeURIComponent((document.querySelector(isSearchMenuOpen ? '.search-menu select[name*="in_folder"]' : '#folder_name') as HTMLSelectElement).value);
        const offset = 0;
        const search = encodeURIComponent((document.getElementById('search') as HTMLInputElement).value);
        return `folder=${folder}&offset=0&search=${search}`;
    }

    async function handleGetEmails(event: Event){
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        getEmailButton.disabled = true;
        getEmailButton.textContent = 'Loading...';
        let response: OpenMailData;
        let searchMenuValues: SearchCriteria | "" = "";
        if(typeof getSearchMenuValues === 'function')
            searchMenuValues = getSearchMenuValues();

        if(isSearchMenuOpen && searchMenuValues != ""){
            response = await fetch(
                `${get(serverUrl)}/search-emails`
                , {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        folder: (document.querySelector('.search-menu select[name*="in_folder"]') as HTMLSelectElement).value,
                        search: searchMenuValues,
                        offset: 0
                    })
                }
            ).then(res => res.json());
        }
        else{
            response = await fetch(
                `${get(serverUrl)}/get-emails/?${getFormKeyValuesAsString()}`
            ).then(res => res.json());
        }

        if(response.success){
            emails.set(response.data["emails"] as Email[]);
            currentFolder.set(response.data["folder"]);
            currentOffset.set(response.data["total"] < 10 ? response.data["total"] : 10);
            totalEmailCount.set(response.data["total"]);
        }
        getEmailButton.disabled = false;
        getEmailButton.textContent = isSearchMenuOpen ? "Search Emails" : "Get Emails";
    }
</script>

<section class="get-emails">
    <div class="card">
        <form id="get-emails-form" on:submit={handleGetEmails}>
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <select name="email_address" id="email_address" required>
                    {#each $accounts as currentAccount}
                        <option value={currentAccount.email} selected>{currentAccount.email}</option>
                    {/each}
                </select>
            </div>
            <div class="form-group">
                <label for="folder">Folder</label>
                <select name="folder_name" id="folder_name">
                    {#if $folders && $folders.length > 0}
                        {#each $folders as folder}
                            <option value={folder}>{folder}</option>
                        {/each}
                    {/if}
                </select>
            </div>
            <div class="form-group">
                <label for="search">Search</label>
                <div class="input-group">
                    <input type="text" name="search" id="search" placeholder="Subject or Person">
                    <button type="button" on:click={toggleSearchMenu}>∨</button>
                </div>
                {#if isSearchMenuOpen}
                    <SearchMenu bind:getSearchMenuValues={getSearchMenuValues} />
                {/if}
            </div>
            <button type="submit">{isSearchMenuOpen ? "Search Emails" : "Get Emails"}</button>
        </form>
    </div>
</section>
