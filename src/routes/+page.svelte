<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Register from "$lib/components/Register.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import Content from "$lib/components/Content.svelte";
    import Compose from "$lib/components/Compose.svelte";
    import SearchBar from "$lib/components/SearchBar.svelte";
    import { SharedStore, SharedStoreKeys } from "$lib/stores/shared.svelte";
    import { ApiService, PostRoutes, type PostResponse } from "$lib/services/ApiService";
    import { mount, onMount, unmount } from "svelte";
    import type { EmailWithContent } from "$lib/types";

    let isLoading: boolean = $derived(SharedStore.server === "");
    let mountedInbox: Record<string, any>;
    let mountedCompose: Record<string, any>;
    let mountedContent: Record<string, any>;

    $effect(() => {
        if (SharedStore.mailboxes.length > 0) {
            showInbox();
        }
    })

    async function removeAllAccounts() {
        const response: PostResponse = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNTS,
			{}
        );

        if (response.success) {
            SharedStore.reset(SharedStoreKeys.accounts);
        } else {
            alert(response.message);
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
        } else {
            alert(response.message);
        }
    }

    async function resetFileSystem() {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RESET_FILE_SYSTEM,
            {}
        );

        alert(response.message);
    }

    function showCompose() {
        unmount(mountedInbox);
        unmount(mountedContent);
        mountedCompose = mount(Compose, { target: document.getElementById("content")! });
    }

    function showContent(email: EmailWithContent) {
        unmount(mountedInbox);
        unmount(mountedCompose);
        mountedContent = mount(Content, {
            target: document.getElementById("content")!,
            props: { email }
        });
    }

    function showInbox(){
        unmount(mountedContent);
        unmount(mountedCompose);
        mountedInbox = mount(Inbox, {
            target: document.getElementById("content")!,
            props: { showContent }
        });
    }
</script>

{#if SharedStore.mailboxes.length > 0}
    <main>
        <section style="width:20%;margin-right:5px;">
            <Sidebar {showCompose} />
        </section>
        <section style="width:80%;">
            <SearchBar />
            <div id="content"></div>
        </section>
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
