<script lang="ts">
    import { onMount } from 'svelte';

    let searchMenu: HTMLElement;
    onMount(() => {
        searchMenu = document.querySelector('.search-menu')!;
    });

    function showSearchMenu(){
        searchMenu.classList.toggle('show');
    }
</script>

<section class="get-emails">
    <div class="card">
        <form id="get-emails-form">
            <div class="form-group">
                <label for="email_address">Email Address</label>
                <input type="email" name="email_address" id="email_address" required>
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
                    <div class="row">
                        <div class="form-group">
                            <label for="has_attachments">Has Attachment(s)</label>
                            <div class="input-group">
                                <input type="checkbox" name="has_attachments" id="has_attachments">
                                <label for="has_attachments">Yes</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="flags">Include Flag</label>
                            <div class="row">
                                <div class="column" style="align-items:start;">
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Seen">
                                        <label for="flags">Seen</label>
                                    </div>
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Answered">
                                        <label for="flags">Answered</label>
                                    </div>
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Flagged">
                                        <label for="flags">Flagged</label>
                                    </div>
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Draft">
                                        <label for="flags">Draft</label>
                                    </div>
                                </div>
                                <div class="column" style="align-items:start;">
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Unseen">
                                        <label for="flags">Unseen</label>
                                    </div>
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Unanswered">
                                        <label for="flags">Unanswered</label>
                                    </div>  
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Unflagged">
                                        <label for="flags">Unflagged</label>
                                    </div>
                                    <div class="input-group">
                                        <input type="checkbox" name="flags" value="Undraft">
                                        <label for="flags">Undraft</label>
                                    </div>
                                </div>
                            </div>
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
                </div>
            </div>
            <input type="hidden" name="operation" value="get-emails">
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

        & .row{
            justify-content: space-between;
            width: 100%;
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
    }
</style>