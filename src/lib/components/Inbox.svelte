<script lang="ts">
    import InboxItem from './Inbox/InboxItem.svelte';
    import { emails, currentFolder, totalEmailCount } from '$lib/stores';

    let offsetEnd = 10;
</script>

<section class = "card">
    <div class="inbox-header">
        <h3>{$currentFolder}</h3>
        <hr>
        <div class="inbox-pagination">
            <button>Previous</button>
            <small>{offsetEnd - 9} - {offsetEnd} of {$totalEmailCount}</small>
            <button>Next</button>
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