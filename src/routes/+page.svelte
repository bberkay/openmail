<script lang="ts">
    import Register from "$lib/components/Register.svelte";
    import type { Response } from "$lib/types";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import Inbox from "$lib/components/Inbox.svelte";

    let isLoading: boolean = $state(true);

    $effect(() => {
        if (sharedStore.server && sharedStore.accounts.length === 0 && isLoading)
            fetchAccounts();
        else
            isLoading = false;
    });

    async function fetchAccounts(): Promise<void> {
        const response: Response = await fetch(
            `${sharedStore.server}/get-email-accounts`,
        ).then((res) => res.json());
        if (Object.hasOwn(response, "data") && response.data) {
            sharedStore.accounts = response.data;
        }
        isLoading = false;
    }
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if sharedStore.inboxes.length > 0}
    <main class="container">
        <div class="sidebar-container">
            <!--<Sidebar />-->
        </div>
        <div class="inbox-container">
            <Inbox />
        </div>
        <div class="email-container">
            <!--<Content />-->
        </div>
    </main>
    <pre>{JSON.stringify(sharedStore, null, 2)}</pre>
{:else if isLoading}
    <p>Loading</p>
{:else}
    <Register/>
{/if}

<style>
    pre {
        overflow: scroll;
        height: 85vh;
        background-color: #333;
        border:1px solid #3a3a3a;
        color: #f5f5f5;
        padding: 10px;
        margin: 0;
        font-size: 12px;
        font-family: monospace;
    }

    .container {
        display: flex;
    }

    .sidebar-container {
        width: 25%;
    }

    .inbox-container {
        width: 35%;
    }

    .email-container {
        width: 40%;
    }
</style>
