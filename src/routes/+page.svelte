<script lang="ts">
    import Loader from "$lib/components/Elements/Loader.svelte";
    import Inbox from "$lib/components/Inbox/Inbox.svelte";
    import Register from "$lib/components/Register/Register.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import SearchBar from "$lib/components/Inbox/SearchBar.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/components/Main.svelte";
    import Content from "$lib/components/Content.svelte";
    import MainSidebar from "$lib/components/Sidebar/MainSidebar.svelte";
    import Layout from "$lib/components/Layout.svelte";
    import Navbar from "$lib/components/Navbar.svelte";
    import Account from "$lib/components/Navbar/Account.svelte";

    let isLoading: boolean = $derived(SharedStore.server === "");
</script>

<Layout>
    {#if SharedStore.mailboxes.length > 0}
        <Main>
            <Navbar>
                <Account />
            </Navbar>
            <div class="mailbox">
                <section style="width:20%;margin-right:5px;">
                    <Sidebar >
                        <MainSidebar />
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
    {:else if isLoading}
        <Loader />
    {:else}
        <Register />
    {/if}
</Layout>

<hr />
<pre>{SharedStore.toString()}</pre>

<style>
    .mailbox {
        display: flex;
    }
</style>
