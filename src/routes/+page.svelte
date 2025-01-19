<script lang="ts">
    import Loader from "$lib/components/Elements/Loader.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Register from "$lib/components/Register.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import Content from "$lib/components/Content.svelte";
    import Compose from "$lib/components/Compose.svelte";
    import SearchBar from "$lib/components/SearchBar.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { EmailWithContent } from "$lib/types";

    let isLoading: boolean = $derived(SharedStore.server === "");
    let isInboxShown: boolean = $state(true);
    let isComposeShown: boolean = $state(false);
    let shownEmail: EmailWithContent | null = $state(null);

    const showCompose = () => {
        clearContent();
        isComposeShown = true;
    }

    const showContent = (email: EmailWithContent) => {
        clearContent();
        shownEmail = email;
    }

    const showInbox = () => {
        clearContent();
        isInboxShown = true;
    }

    const clearContent = () => {
        if (isInboxShown) isInboxShown = false;
        if (isComposeShown) isComposeShown = false;
        if (shownEmail) shownEmail = null;
    }
</script>

{#if SharedStore.mailboxes.length > 0}
    <main>
        <section style="width:20%;margin-right:5px;">
            <Sidebar {showCompose} />
        </section>
        <section style="width:80%;">
            <SearchBar />
            <div class="card">
                {#if isInboxShown}
                    <Inbox {showContent} />
                {:else if isComposeShown}
                    <Compose {showInbox} />
                {:else if shownEmail}
                    <button onclick={showInbox}>Back</button>
                    <Content email={shownEmail} />
                {/if}
            </div>
        </section>
    </main>
{:else if isLoading}
    <Loader />
{:else}
    <Register />
{/if}

<hr />
<pre>{SharedStore.toString()}</pre>
