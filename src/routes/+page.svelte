<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Settings from "$lib/ui/Layout/Main/Content/Settings.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Welcome from "$lib/ui/Layout/Landing/Register/Welcome.svelte";
    import Accounts from "$lib/ui/Layout/Landing/Register/Accounts.svelte";

    let isAnyAccountFound = $derived(SharedStore.accounts.length > 0 || SharedStore.failedAccounts.length > 0);
</script>

{#if Object.keys(SharedStore.mailboxes).length > 0}
    <Main>
        <Navbar />
        <Content>
            <!--<Mailbox />-->
            <Settings />
        </Content>
    </Main>
{:else}
    <Landing>
        <Register>
            {#if isAnyAccountFound}
                <Accounts />
            {:else}
                <Welcome/>
            {/if}
        </Register>
    </Landing>
{/if}
