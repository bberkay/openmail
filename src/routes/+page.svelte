<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
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
        <Register />
    </Landing>
{/if}
