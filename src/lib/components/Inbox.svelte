<script lang="ts">
    import InboxItem from './Inbox/InboxItem.svelte';

    export let inbox_data: any;
    let inboxName = inbox_data.folder.slice(0, 1).toUpperCase() + inbox_data.folder.slice(1);
    let totalEmailCount: number = inbox_data.total;
    let offsetEnd: number = 10;
    let emails = inbox_data.emails;
</script>

<section class = "card">
    <div class="inbox-header">
        <h2>{inboxName}</h2>
        <hr>
        <div class="inbox-pagination">
            <button>Previous</button>
            <small>{offsetEnd - 10} - {offsetEnd} of {totalEmailCount}</small>
            <button>Next</button>
        </div>
        <hr>
    </div>
    <div class="inbox-content">
        {#each emails as email}
            <InboxItem email={email} folder={inboxName}/>
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
        max-height: 85vh;
        overflow-y: auto;
        
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