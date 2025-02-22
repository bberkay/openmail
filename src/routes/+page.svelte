<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import SearchBar from "$lib/ui/Layout/Main/Navbar/SearchBar.svelte";
    import Sidebar from "$lib/ui/Layout/Main/Sidebar.svelte";
    import FolderMenu from "$lib/ui/Layout/Main/Sidebar/FolderMenu.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Loading from "$lib/ui/Layout/Landing/Loading.svelte";

    let isLoading: boolean = $derived(SharedStore.server === "");
</script>

{#if SharedStore.mailboxes.length > 0}
    <Main>
        <div class="mailbox">
            <section style="width:20%;margin-right:5px;">
                <Sidebar>
                    <Account />
                    <FolderMenu />
                </Sidebar>
            </section>
            <section style="width:80%;">
                <SearchBar />
                <div class="card">
                    <Content>
                        <Inbox />
                    </Content>
                </div>
            </section>
        </div>
    </Main>
{:else}
    <Landing>
        {#if isLoading}
            <Loading />
        {:else}
            <Register />
        {/if}
    </Landing>
{/if}

<style>
    .mailbox {
        display: flex;
    }
</style>
