<script lang="ts">
    import { sharedStore } from "$lib/stores/shared.svelte";
    import { ApiService, GetRoutes, PostRoutes, type Response } from "$lib/services/ApiService";

	let { children } = $props();

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
            sharedStore.inboxes = [];
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

<div class = "container">
	{@render children()}
</div>

<hr>
<button onclick={deleteAllAccounts}>Delete All Accounts</button>
<button onclick={resetFileSystem}>Reset File System</button>
<button onclick={recreateWholeUniverse}>Recreate whole universe</button>

<style>
	.container {
		padding: 5px;
	}
</style>
