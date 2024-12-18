<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Register from "$lib/components/Register.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import { sharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, PostRoutes, type Response } from "$lib/services/ApiService";

    let isLoading: boolean = $derived(sharedStore.server === "");

    async function deleteAllAccounts() {
        const response: Response = await ApiService.post(
            sharedStore.server,
            PostRoutes.DELETE_EMAIL_ACCOUNTS,
			{}
        );

        if (response.success) {
            sharedStore.accounts = [];
        }
    }

	async function recreateWholeUniverse() {
        const response = await ApiService.post(
            sharedStore.server,
            PostRoutes.REFRESH_WHOLE_UNIVERSE,
            {}
        );

        if (response.success) {
            sharedStore.server = "";
            sharedStore.accounts = [];
            sharedStore.mailboxes = [];
            sharedStore.folders = [];
            sharedStore.selectedAccounts = [];
            sharedStore.selectedFolder = "Inbox";
            sharedStore.selectedEmail = null;
            sharedStore.currentOffset = 0;
        }
    }

    async function resetFileSystem() {
        const response = await ApiService.post(
            sharedStore.server,
            PostRoutes.RESET_FILE_SYSTEM,
            {}
        );

        if (response.success) {
            // Show an alert.
        }
    }
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if sharedStore.mailboxes.length > 0}
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
<pre>{JSON.stringify(sharedStore, null, 2)}</pre>

<hr>
<div style="text-align: center;">
    <button onclick={deleteAllAccounts}>Delete All Accounts</button>
    <button onclick={resetFileSystem}>Reset File System</button>
    <button onclick={recreateWholeUniverse}>Recreate whole universe</button>
</div>

<style>
    main {
        width: 100%;
        display:flex;

        & section {
            margin: 10px;
        }
    }
</style>
