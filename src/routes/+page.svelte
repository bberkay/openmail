<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Layout from "$lib/ui/Layout/Layout.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Account from "$lib/ui/Layout/Navbar/Account.svelte";
    import SearchBar from "$lib/ui/Layout/Navbar/SearchBar.svelte";
    import Sidebar from "$lib/ui/Layout/Main/Sidebar.svelte";
    import FolderMenu from "$lib/ui/Layout/Main/Sidebar/FolderMenu.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Spinner from "$lib/ui/Elements/Loader";

    let isLoading: boolean = $derived(SharedStore.server === "");
</script>

<Layout>
    {#if SharedStore.mailboxes.length > 0}
        <Main>
            <Navbar>
                <Account />
                <SearchBar />
            </Navbar>
            <div class="mailbox">
                <section style="width:20%;margin-right:5px;">
                    <Sidebar>
                        <FolderMenu />
                    </Sidebar>
                </section>
                <section style="width:80%;">
                    <div class="card">
                        <Content>
                            <Inbox />
                        </Content>
                    </div>
                </section>
            </div>
        </Main>
    {:else if isLoading}
        <Spinner />
    {:else}
        <Landing>
            <Register />
        </Landing>
    {/if}
</Layout>

<hr />
<pre>{SharedStore.toString()}</pre>

<style>
    .mailbox {
        display: flex;
    }
</style>
