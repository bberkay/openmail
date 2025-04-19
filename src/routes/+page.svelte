<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { onMount } from "svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import Main from "$lib/ui/Layout/Main.svelte";
    import Navbar from "$lib/ui/Layout/Main/Navbar.svelte";
    import Content from "$lib/ui/Layout/Main/Content.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Landing from "$lib/ui/Layout/Landing.svelte";
    import Register from "$lib/ui/Layout/Landing/Register.svelte";
    import Loading from "$lib/ui/Layout/Landing/Register/Loading.svelte";
    import Welcome from "$lib/ui/Layout/Landing/Register/Welcome.svelte";

    let isServerLoading = $derived(SharedStore.server === "");

    onMount(async () => {
        const response = await AccountController.init();
        if(!response.success) {
            console.error(response.message);
            showMessage({
                title: local.error_initialize_accounts[DEFAULT_LANGUAGE],
            });
        }
    })
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
            {:else}
                <Welcome/>
            {/if}
        </Register>
    </Landing>
{/if}
