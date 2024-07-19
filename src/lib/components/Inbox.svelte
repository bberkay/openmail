<script lang="ts">
    import InboxItem from './Inbox/InboxItem.svelte';
    import { emails, currentFolder, totalEmailCount, currentOffset } from '$lib/stores';
    import { get } from 'svelte/store';
    import { onMount } from 'svelte';
    import type { OpenMailData } from '$lib/types';

    let prevButton: HTMLButtonElement;
    let nextButton: HTMLButtonElement;
    onMount(() => {
        prevButton = document.getElementById('prev-button') as HTMLButtonElement;
        nextButton = document.getElementById('next-button') as HTMLButtonElement;

        currentOffset.subscribe(async (value) => {
            if(value <= 0)
                return;

            /**
             * If user moves email to another folder, the offset will not be a multiple of 10.
             * In this case, we need to fetch the emails from the previous page to complete the page.
             * For example, if the offset is 13, we need to fetch the emails from 10 to 20. 
             * This is not a good solution but it is enough for now.
             */
            const complete_to_ten = $currentOffset - $currentOffset % 10;
            if(complete_to_ten != $currentOffset){
                let response: OpenMailData = await fetch(
                    `http://127.0.0.1:8000/get-emails/?folder=${get(currentFolder)}&offset=${complete_to_ten.toString()}&search=${getSearchMenuValue()}`
                ).then(response => response.json());
                if(response.success){
                    emails.set(response.data["emails"]);
                    currentOffset.update(value => 10 + complete_to_ten);
                }
            }
        });
    });

    function getSearchMenuValue(){
        // TODO: This is a temporary solution until the offset system is improved.
        const search = (document.getElementById('search') as HTMLInputElement).value;
        return search.trim() == "" ? "" : `OR (OR (FROM "${search}") (TO "${search}")) (SUBJECT "${search}")`;
    }

    async function getPreviousEmails(){
        if(get(currentOffset) <= 10)
            return;

        prevButton.disabled = true;
        let response: OpenMailData = await fetch(
            `http://127.0.0.1:8000/get-emails/?folder=${get(currentFolder)}&offset=${(get(currentOffset) - 20)}&search=${getSearchMenuValue()}`
        ).then(response => response.json());
        if(response.success){
            currentOffset.update(value => value - 10);
            emails.set(response.data["emails"]);
        }
        prevButton.disabled = false;
    }

    async function getNextEmails(){
        if(get(currentOffset) >= get(totalEmailCount))
            return;

        nextButton.disabled = true;
        let response: OpenMailData = await fetch(
            `http://127.0.0.1:8000/get-emails/?folder=${get(currentFolder)}&offset=${get(currentOffset)}&search=${getSearchMenuValue()}`
        ).then(response => response.json());
        if(response.success){
            currentOffset.update(value => value + 10);
            emails.set(response.data["emails"]);
        }
        nextButton.disabled = false;
    }
</script>

<section class = "card">
    <div class="inbox-header">
        <h2>{$currentFolder == "inbox" ? "Inbox" : $currentFolder}</h2>
        <hr>
        <div class="inbox-pagination">
            <button id="prev-button" on:click={getPreviousEmails} disabled={$currentOffset <= 10}>Previous</button>
            <small>{Math.max(1, $currentOffset - 9)} - {$currentOffset} of {$totalEmailCount}</small>
            <button id="next-button" on:click={getNextEmails} disabled={$currentOffset >= $totalEmailCount}>Next</button>
        </div>
        <hr>
    </div>
    <div class="inbox-content">
        {#each $emails as email}
            <InboxItem email={email}/>
        {/each}
    </div>
</section>

<style>
    .inbox-pagination{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .inbox-content{
        & h3{
            margin: 0;
        }

        & .inbox-item:first-child{
            padding-top:0.5rem;
        }

        & .inbox-item:last-child{
            border-bottom: none;
        }
    }
</style>