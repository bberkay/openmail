<script lang="ts">
    import InboxItem from './Inbox/InboxItem.svelte';
    import { emails, currentFolder, totalEmailCount } from '$lib/stores';
    import { invoke } from '@tauri-apps/api/core';
    import { get } from 'svelte/store';
    import { onMount } from 'svelte';
    import type { OpenMailDataString, OpenMailData } from '$lib/types';


    let offsetEnd = 10;
    let prevButton: HTMLButtonElement;
    let nextButton: HTMLButtonElement;
    onMount(() => {
        prevButton = document.getElementById('prev-button') as HTMLButtonElement;
        nextButton = document.getElementById('next-button') as HTMLButtonElement;
    });

    async function getPreviousEmails(e: Event){
        if(offsetEnd < 10)
            return;

        prevButton.disabled = true;
        let response: OpenMailDataString = await invoke('get_emails', { offset: (offsetEnd - 20).toString() });
        let parsedResponse: OpenMailData = JSON.parse(response);
        if(parsedResponse.success){
            offsetEnd -= 10;
            emails.set(parsedResponse.data["emails"]);
        }
        prevButton.disabled = false;
    }

    async function getNextEmails(){
        if(offsetEnd >= get(totalEmailCount))
            return;

        nextButton.disabled = true;
        let response: OpenMailDataString = await invoke('get_emails', { offset: offsetEnd.toString() });
        let parsedResponse: OpenMailData = JSON.parse(response);
        if(parsedResponse.success){
            offsetEnd += 10;
            emails.set(parsedResponse.data["emails"]);
        }
        nextButton.disabled = false;
    }
</script>

<section class = "card">
    <div class="inbox-header">
        <h3>{$currentFolder}</h3>
        <hr>
        <div class="inbox-pagination">
            <button id="prev-button" on:click={getPreviousEmails}>Previous</button>
            <small>{offsetEnd - 9} - {offsetEnd} of {get(totalEmailCount)}</small>
            <button id="next-button" on:click={getNextEmails}>Next</button>
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