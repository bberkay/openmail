<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Loading from "$lib/ui/Layout/Landing/Register/Loading.svelte";
    import Welcome from "$lib/ui/Layout/Landing/Register/Welcome.svelte";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";

    let isServerLoading = $derived(SharedStore.server === "");
    let isAnyAccountFound = $derived(SharedStore.accounts.length > 0 || SharedStore.failedAccounts.length > 0);
</script>

{#if Object.keys(SharedStore.mailboxes).length > 0}
    <Main>
        <Navbar />
        <Content>
            <Mailbox />
        </Content>
    </Main>
{:else}
    <Landing>
        <Register>
            {#if isServerLoading}
                <Loading/>
            {:else if isAnyAccountFound}
                <AccountList />
            {:else}
                <Welcome/>
            {/if}
        </Register>
    </Landing>
{/if}
