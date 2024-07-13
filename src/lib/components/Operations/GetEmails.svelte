<script lang="ts">
    import { onMount } from 'svelte';
    import { invoke } from "@tauri-apps/api/core";
    import { emails, currentFolder, totalEmailCount } from '$lib/stores';
    import type { Email, OpenMailData, OpenMailDataString } from '$lib/types';
    import { get } from 'svelte/store';

    let searchMenu: HTMLElement;
    let getEmailForm: HTMLFormElement;
    let getEmailButton: HTMLButtonElement;
    onMount(() => {
        searchMenu = document.querySelector('.search-menu')!;
        getEmailForm = document.getElementById('get-emails-form') as HTMLFormElement;
        getEmailButton = getEmailForm.querySelector('button[type="submit"]') as HTMLButtonElement;
    });

    function showSearchMenu(){
        searchMenu.classList.toggle('show');
    }

    function getFormKeyValues(){
        return Object.fromEntries(new FormData(getEmailForm).entries());
    }

    async function handleGetEmails(event: Event){ 
        event.preventDefault();
        const form = event.target;
        if (!(form instanceof HTMLFormElement))
            return;

        getEmailButton.disabled = true;
        getEmailButton.textContent = 'Loading...';
        console.log(getFormKeyValues());
        /*let response: OpenMailDataString = await invoke('get_emails', getFormKeyValues());
        try{
            let parseResponse = JSON.parse(response) as OpenMailData;
            if(parseResponse.success){
                emails.set(parseResponse.data["emails"] as Email[]);
                currentFolder.set(parseResponse.data["folder"]);
                totalEmailCount.set(parseResponse.data["total"]);
            }
        }catch{
            console.error(response);
        }*/
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
                    <input type="text" name="search" id="search">
                    <button type="button" on:click={showSearchMenu}>⇅</button>
                </div>
                <div class="search-menu">
                    <div class="row">
                        <div class="form-group">
                            <label for="from">From</label>
                            <input type="text" name="from" id="from">
                            <div class="tags">
                                <!-- Emails -->
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="to">To</label>
                            <input type="text" name="to" id="to">
                            <div class="tags">
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
                            <label for="start_date">Start Date</label>
                            <input type="date" name="start_date" id="start_date">
                        </div>
                        <div class="form-group">
                            <label for="end_date">End Date</label>
                            <input type="date" name="end_date" id="end_date">
                        </div>
                    </div>
                    <div class="column">
                        <div class="form-group">
                            <label for="flags">Include Flag</label>
                            <div class="input-group">
                                <select name="flags" id="flags">
                                    <optgroup>
                                        <option value="Seen">Seen</option>
                                        <option value="Answered">Answered</option>
                                        <option value="Flagged">Flagged</option>
                                        <option value="Draft">Draft</option>
                                    </optgroup>
                                    <optgroup>
                                        <option value="Unseen">Unseen</option>
                                        <option value="Unanswered">Unanswered</option>
                                        <option value="Unflagged">Unflagged</option>
                                        <option value="Undraft">Undraft</option>
                                    </optgroup>
                                </select>
                                <button>+</button>
                            </div>
                        </div>
                        <div class="tags">
                            <!-- Flags -->
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="in_folder">In Folder</label>
                        <select name="in_folder" id="in_folder"></select>
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
            </div>
            <button type="submit">Get Emails</button>
        </form>
    </div>
</section>

<style>
    .search-menu{
        background-color: #444;
        border: 1px solid #5a5a5a;
        padding: 10px;
        margin-top: 5px;
        display: none;
        justify-content: space-between;
        flex-direction: column;
        box-shadow: 0 0 10px #202020;
        border-radius: 5px;

        &.show{
            display: flex;
        }

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