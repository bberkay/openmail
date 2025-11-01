<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Mailbox, { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Welcome from "$lib/ui/Layout/Landing/Register/Welcome.svelte";
    import Accounts from "$lib/ui/Layout/Landing/Register/Accounts.svelte";
    import SetupServer from "$lib/ui/Layout/Landing/Register/SetupServer.svelte";

    let isConnectedToServer = $derived(SharedStore.server.length > 0);
    let isAnyAccountFound = $derived(SharedStore.accounts.length > 0 || SharedStore.failedAccounts.length > 0);
    let isMailboxInitialized = $derived(Object.keys(SharedStore.mailboxes).length > 0 && getCurrentMailbox());
</script>

{#if isMailboxInitialized}
    <Main>
        <Navbar />
        <Content>
            <Mailbox />
        </Content>
    </Main>
{:else}
    <Landing>
        <Register>
            {#if isAnyAccountFound}
                <Accounts />
            {:else if isConnectedToServer}
                <Welcome/>
            {:else}
                <SetupServer/>
            {/if}
        </Register>
    </Landing>
{/if}
