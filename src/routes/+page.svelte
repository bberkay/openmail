<script lang="ts">
    import Register from "$lib/components/Register.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";

    let isLoading: boolean = $derived(sharedStore.server === "");
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if sharedStore.inboxes.length > 0}
    <!--
    <main>
        <section>
            <Sidebar />
        </section>
        <section>
            <Inbox />
        </section>
        <section>
            <Content />
        </section>
    </main>
    -->
{:else if isLoading}
    <span><small class="loader"></small> Loading</span>
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

    .loader {
        border: 2px solid #2a2a2a;
        border-radius: 50%;
        border-top: 2px solid #fff;
        width: 10px;
        height: 10px;
        -webkit-animation: spin 2s linear infinite;
        animation: spin 2s linear infinite;
        display: inline-block;
        margin-right: 5px;
    }

    @-webkit-keyframes spin {
        0% { -webkit-transform: rotate(0deg); }
        100% { -webkit-transform: rotate(360deg); }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    pre {
        overflow: scroll;
        max-height: 50vh;
        padding: 10px;
        margin: 0;
        font-size: 12px;
        font-family: monospace;
        background-color: #222222;
        color: #f8f8f8;
        border-radius: 5px;
        border: 1px solid #3a3a3a;
    }
</style>
