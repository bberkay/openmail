<script lang="ts">
    import InboxItem from './Inbox/InboxItem.svelte';

    export let inboxName = "Inbox";
    export let emails = [
        {
            from: "From",
            date: "03/03/2021",
            to: "someone@mail.com",
            subject: "A Very Important Email",
            body: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Illo, illum. Odio beatae, aperiam cupiditate",
            flags: "Seen"
        },
        {
            from: "From",
            date: "03/03/2022",
            to: "god@mail.com",
            subject: "Lorem Ipsum Dolor Sit Amet",
            body: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Illo, illum. Odio beatae, aperiam cupiditate",
            flags: "Flagged"
        },
        {
            from: "From",
            date: "03/03/2023",
            to: "me@mail.com",
            subject: "Most Important Email",
            body: "Lorem ipsum dolor sit amet consectetur adipisicing elit. Illo, illum. Odio beatae, aperiam cupiditate",
            flags: ""
        }
    ];
</script>

<section class = "card">
    <div class="inbox-header">
        <h2>{inboxName}</h2>
        <hr>
        <div class="inbox-pagination">
            <button>Previous</button>
            <small>15 - 35 of 1792</small>
            <button>Next</button>
        </div>
        <hr>
    </div>
    <div class="inbox-content">
        {#each emails as email}
            <InboxItem {email}/>
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