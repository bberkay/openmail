<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Register from "$lib/components/Register.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { SharedStore, SharedStoreKeys } from "$lib/stores/shared.svelte";
    import { ApiService, PostRoutes, type PostResponse } from "$lib/services/ApiService";

    let isLoading: boolean = $derived(SharedStore.server === "");

    async function removeAllAccounts() {
        const response: PostResponse = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNTS,
			{}
        );

        if (response.success) {
            SharedStore.reset(SharedStoreKeys.accounts);
        }
    }

	async function recreateWholeUniverse() {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RECREATE_WHOLE_UNIVERSE,
            {}
        );

        if (response.success) {
            SharedStore.reset();
        }
    }

    async function resetFileSystem() {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RESET_FILE_SYSTEM,
            {}
        );

        if (response.success) {
            // Show an alert.
        }
    }
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if SharedStore.mailboxes.length > 0}
    <main>
        <section>
            <Sidebar />
        </section>
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
<pre>{SharedStore.toString()}</pre>

<hr>
<div style="text-align: center;">
    <button onclick={removeAllAccounts}>Delete All Accounts</button>
    <button onclick={resetFileSystem}>Reset File System</button>
    <button onclick={recreateWholeUniverse}>Recreate whole universe</button>
</div>

<style>
    main {
        width: 100%;
        background-color: #2e2e2e;
        padding: 5px;
        border-radius: 5px;
        border:1px solid #5a5a5a;
        box-sizing: border-box;

        & section {
            margin: 10px;
        }
    }
</style>
