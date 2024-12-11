<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Register from "$lib/components/Register.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";

    let isLoading: boolean = $derived(sharedStore.server === "");
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if sharedStore.mailboxes.length > 0}
    <main>
        <!--<section>
            <Sidebar />
        </section>-->
        <section>
            <Inbox />
        </section>
        <!--<section>
            <Content />
        </section>-->
    </main>
{:else if isLoading}
    <Loader />
{:else}
    <Register/>
{/if}

<hr>

<pre>{JSON.stringify(sharedStore, null, 2)}</pre>

<style>
    main {
        width: 100%;
        display:flex;

        & section {
            margin: 10px;
        }
    }
</style>
