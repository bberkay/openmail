<script lang="ts">
    import { onMount } from "svelte";
    import {
        emails,
        currentFolder,
        folders,
        currentOffset,
        serverUrl,
        accounts,
        currentAccounts,
    } from "$lib/stores";
    import type { Email, Response, SearchCriteria } from "$lib/types";
    import SearchMenu from "./SearchMenu.svelte";
    import { get } from "svelte/store";

    let selectedAccount: string = get(accounts)[0].email;
    let selectedAccounts: string[] = [];
    let getSearchMenuValues: () => SearchCriteria | "";
    let isSearchMenuOpen = false;
    let getEmailForm: HTMLFormElement;
    let getEmailButton: HTMLButtonElement;
    onMount(() => {
        getEmailForm = document.getElementById(
            "get-emails-form",
        ) as HTMLFormElement;
        getEmailButton = getEmailForm.querySelector(
            'button[type="submit"]',
        ) as HTMLButtonElement;
    });

    function selectAccount(event: Event): void {
        selectedAccount = (event.target as HTMLSelectElement).value;
    }

    function toggleSearchMenu(e: Event) {
        isSearchMenuOpen = !isSearchMenuOpen;
        (e.target as HTMLButtonElement).textContent = isSearchMenuOpen
            ? "X"
            : "∨";
    }

    function getFormKeyValuesAsString() {
        let emails: string = Array.from(document.querySelector(".tags#accounts")!.querySelectorAll("span")).join(", ");
        if(emails === "") emails = get(accounts).map((account) => account.email).join(", ");
        const folder = encodeURIComponent(
            (
                document.querySelector(
                    isSearchMenuOpen
                        ? '.search-menu select[name*="in_folder"]'
                        : "#folder_name",
                ) as HTMLSelectElement
            ).value,
        );
        const offset = 0;
        const search = encodeURIComponent(
            (document.getElementById("search") as HTMLInputElement).value,
        );
        return `${emails}?folder=${folder}&offset=0&search=${search}`;
    }

    function handleMultipleSelectOption(selectId: string, formId: string){
        const select = document.querySelector(`#${selectId}`) as HTMLSelectElement;
        const tags = document.querySelector(`#${formId}`) as HTMLDivElement;
        tags.style.display = 'flex';
        if(select.value !== ''){
            tags.innerHTML += `<span>${select.value}<button onclick="this.parentElement.remove()"></button></span>`;
            select.value = '';
        }
    }

    async function handleGetEmails(event: Event) {
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;

        getEmailButton.disabled = true;
        getEmailButton.textContent = "Loading...";

        let response: Response;
        selectedAccounts = Array.from(document.querySelector(".tags#accounts")!.querySelectorAll("span")).map((span) => { return span.textContent || ""; });
        if(selectedAccounts.length == 0){
            if(get(currentAccounts).length > 0) selectedAccounts = get(currentAccounts).map((account) => account.email);
            else selectedAccounts = get(accounts).map((account) => account.email);
        }
        const searchMenuValues: SearchCriteria | "" = typeof getSearchMenuValues === "function" ? getSearchMenuValues() : "";
        const folder = encodeURIComponent(
            selectedAccounts.length > 1 ? "INBOX" : (
                document.querySelector(
                    isSearchMenuOpen
                        ? '.search-menu select[name*="in_folder"]'
                        : "#folder_name",
                ) as HTMLSelectElement
            ).value,
        );
        const search = isSearchMenuOpen && searchMenuValues != "" ? searchMenuValues : encodeURIComponent(
            (document.getElementById("search") as HTMLInputElement).value,
        );

        response = await fetch(
            `${get(serverUrl)}/get-emails/${selectedAccounts.join(", ")}?folder=${folder}&search=${search}&offset=0`,
        ).then((res) => res.json());

        if (response.success) {
            emails.set(response.data);
            currentAccounts.set(get(accounts).filter((account) => selectedAccounts.includes(account.email)));
            currentFolder.set(folder);
            let totalEmailCount = get(emails).reduce(
                (acc, account) => selectedAccounts.find((a) => a == account.email) ? acc + account.total : acc,
                0,
            );
            currentOffset.set(
                totalEmailCount < 10 ? totalEmailCount : 10,
            );
        }
        getEmailButton.disabled = false;
        getEmailButton.textContent = isSearchMenuOpen
            ? "Search Emails"
            : "Get Emails";
    }
</script>

<section class="get-emails">
    <div class="card">
        <form id="get-emails-form" on:submit={handleGetEmails}>
            <div class="column">
                <div class="form-group">
                    <label for="email_address">Email Address</label>
                    <div class="input-group">
                        <select
                            name="email_address"
                            id="email_address"
                            on:change={selectAccount}
                            required
                        >
                            {#each $accounts as account}
                                <option value={account.email}>
                                    {account.fullname} &lt;{account.email}&gt;
                                </option>
                            {/each}
                        </select>
                        <button type="button" on:click={() => handleMultipleSelectOption("email_address", "accounts")}>+</button>
                    </div>
                </div>
                <div class="tags" id="accounts">
                    <!-- Accounts -->
                </div>
            </div>
            {#if !isSearchMenuOpen}
            <div class="form-group">
              <label for="folder">Folder</label>
              <select
                name="folder_name"
                id="folder_name"
                disabled={selectedAccounts && selectedAccounts.length > 1}
                required
                >
                {#each $folders as folder}
                  {#if selectedAccount == folder.email}
                    {#each folder.folders as item}
                        <option value={item}>{item}</option>
                    {/each}
                  {/if}
                {/each}
                </select>
            </div>
            {/if}
            <div class="form-group">
                <label for="search">Search</label>
                <div class="input-group">
                    <input
                        type="text"
                        name="search"
                        id="search"
                        placeholder="Subject or Person"
                        disabled={isSearchMenuOpen}
                    />
                    <button type="button" on:click={toggleSearchMenu}>∨</button>
                </div>
                {#if isSearchMenuOpen}
                    <SearchMenu bind:getSearchMenuValues {selectedAccount} {selectedAccounts}/>
                {/if}
            </div>
            <button type="submit">{isSearchMenuOpen ? "Search Emails" : "Get Emails"}</button>
        </form>
    </div>
</section>
