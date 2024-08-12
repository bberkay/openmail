<script lang="ts">
    import { folders } from '$lib/stores';
    import type { SearchCriteria } from '$lib/types';
    import { onMount } from 'svelte';

    export let selectedAccount: string = "";
    export let selectedAccounts: string[] = [];
    let searchMenu: HTMLDivElement;
    onMount(() => {
        searchMenu = document.querySelector('.search-menu')!;
    });

    function handleMultipleTextOption(e: KeyboardEvent, formId: string, regExpMatch: RegExp | null = null){
        const receivers = document.querySelector(`#${formId}`)! as HTMLDivElement;
        receivers.style.display = 'flex';
        const target = e.target as HTMLInputElement;
        if((e.key === 'Spacebar' || e.key === ' ')){
            target.value = target.value.trim();
            if(target.value !== '' && (!regExpMatch || target.value.match(regExpMatch))){
                receivers.style.display = 'flex';
                receivers.innerHTML += `<span>${target.value}<button onclick="this.parentElement.remove()"></button></span>`;
                target.value = '';
            }
            else{
                target.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    target.style.transform = 'scale(1)';
                }, 100);
            }
        }
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

    export function getSearchMenuValues(): SearchCriteria | ""
    {
        const searchMenuData: SearchCriteria = {
            "senders": Array.from(searchMenu.querySelector("#from-email-addresses")!.querySelectorAll("span")).map((span) => { return span.textContent || ""; }),
            "receivers": Array.from(searchMenu.querySelector("#to-email-addresses")!.querySelectorAll("span")).map((span) => { return span.textContent || ""; }),
            "subject": (searchMenu.querySelector("input[name*='subject']") as HTMLInputElement).value,
            "since": (searchMenu.querySelector("input[name*='since']") as HTMLInputElement).value,
            "before": (searchMenu.querySelector("input[name*='before']") as HTMLInputElement).value,
            "flags": Array.from(searchMenu.querySelector("#flags")!.querySelectorAll("span")).map((span) => { return span.textContent || ""; }),
            "include": (searchMenu.querySelector("input[name*='include_words']") as HTMLInputElement).value,
            "exclude": (searchMenu.querySelector("input[name*='exclude_words']") as HTMLInputElement).value,
            "has_attachments": (searchMenu.querySelector("input[name*='has_attachments']") as HTMLInputElement).checked
        };

        // If every key is null or empty and has_attachments is false, return null
        if(Object.values(searchMenuData).every((value) => {
            if(typeof value === 'string')
                return value === '';
            if(Array.isArray(value))
                return value.length === 0;
            if(typeof value === 'boolean')
                return value === false;
        }))
            return "";

        return searchMenuData;
    }
</script>

<div class="search-menu">
    <div class="row">
        <div class="form-group">
            <label for="from">From</label>
            <input type="text" name="from" id="from" on:keyup={(e) => handleMultipleTextOption(e, 'from-email-addresses', /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/)}>
            <div class="tags" id="from-email-addresses">
                <!-- Emails -->
            </div>
        </div>
        <div class="form-group">
            <label for="to">To</label>
            <input type="text" name="to" id="to" on:keyup={(e) => handleMultipleTextOption(e, 'to-email-addresses', /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/)}>
            <div class="tags" id="to-email-addresses">
                <!-- Emails -->
            </div>
        </div>
    </div>
    <div class="form-group">
        <label for="subject">Subject</label>
        <input type="text" name="subject" id="subject">
    </div>
    <div class="row">
        <div class="form-group">
            <label for="since">Since</label>
            <input type="date" name="since" id="since">
        </div>
        <div class="form-group">
            <label for="before">Before</label>
            <input type="date" name="before" id="before">
        </div>
    </div>
    <div class="column">
        <div class="form-group">
            <label for="includes-flags">Includes Flag</label>
            <div class="input-group">
                <select name="includes-flags" id="includes-flags">
                    <optgroup>
                        <option value="Seen">Seen</option>
                        <option value="Answered">Answered</option>
                        <option value="Flagged">Flagged</option>
                        <option value="Draft">Draft</option>
                        <option value="Deleted">Deleted</option>
                    </optgroup>
                    <optgroup>
                        <option value="Unseen">Unseen</option>
                        <option value="Unanswered">Unanswered</option>
                        <option value="Unflagged">Unflagged</option>
                        <option value="Undraft">Undraft</option>
                        <option value="Undeleted">Undeleted</option>
                    </optgroup>
                </select>
                <button type="button" on:click={() => handleMultipleSelectOption("includes-flags", "flags")}>+</button>
            </div>
        </div>
        <div class="tags" id="flags">
            <!-- Flags -->
        </div>
    </div>
    <div class="form-group">
        <label for="in_folder">In Folder</label>
        <select name="in_folder" id="in_folder" disabled={selectedAccounts && selectedAccounts.length > 1}>
            {#each $folders as folder}
              {#if selectedAccount == folder.email}
                {#if $folders && $folders.length > 0}
                  <option value={folder}>{folder}</option>
                {/if}
              {/if}
            {/each}
        </select>
    </div>
    <div class="form-group">
        <label for="include_words">Include Words</label>
        <input type="text" name="include_words" id="include_words">
    </div>
    <div class="form-group">
        <label for="exclude_words">Exclude Words</label>
        <input type="text" name="exclude_words" id="exclude_words">
    </div>
    <div class="form-group">
        <label for="has_attachments">Has Attachment(s)</label>
        <div class="input-group">
            <input type="checkbox" name="has_attachments" id="has_attachments">
            <label for="has_attachments">Yes</label>
        </div>
    </div>
</div>

<style>
    .search-menu{
        background-color: #444;
        border: 1px solid #5a5a5a;
        padding: 10px;
        margin-top: 5px;
        display: flex;
        justify-content: space-between;
        flex-direction: column;
        box-shadow: 0 0 10px #202020;
        border-radius: 5px;

        & input:not(& input[type="checkbox"]), & select{
            margin: 5px 0;
            padding: 5px;
            border-radius: 3px;
            background-color: #747474;
            border: 1px solid #a7a7a7;
            color: #ffffff;

            &:focus:not(& input[type="checkbox"]){
                background-color: #868686;
            }
        }

        & .input-group{
            & select{
                width: 100%;
            }

            & select + button{
                border: 1px solid #a7a7a7;
                padding: 6px;
            }
        }
    }
</style>
