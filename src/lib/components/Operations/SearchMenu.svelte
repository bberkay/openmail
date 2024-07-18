<script lang="ts">
    import { folders } from '$lib/stores';
    import { onMount } from 'svelte';

    let folderSelectOption: HTMLFormElement;
    onMount(() => {
        folderSelectOption = document.querySelector('select[name*="in_folder"]')!;
        folders.subscribe(value => {
            if(value.length > 0){
                value.forEach(folder => {
                    const option = document.createElement('option');
                    option.value = folder;
                    option.innerText = folder;
                    folderSelectOption.appendChild(option);
                });
            }
        })
    });

    export const getSearchMenuValues = () => {
        return ""
    }
</script>

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