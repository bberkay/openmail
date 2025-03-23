<script lang="ts">
    import Folders from "$lib/ui/Layout/Main/Navbar/Folders.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import Search from "$lib/ui/Layout/Main/Navbar/Search.svelte";
    import Notifications from "$lib/ui/Layout/Main/Navbar/Notifications.svelte";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    let navbar: HTMLElement;

    const showCompose = () => {
        showContent(Compose);
    }
</script>

<nav bind:this={navbar}>
    <div class="nav-section">
        <Folders />
        <Search />
    </div>
    <div class="nav-section">
        <Button.Basic
            type="button"
            class="btn-cta nav-button"
            onclick={showCompose}
        >
            <Icon name="compose" />
        </Button.Basic>
        <Account />
        <Notifications />
    </div>
</nav>

<style>
    :global {
        nav {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            width: 100%;
            padding: var(--spacing-lg);

            & .nav-section {
                display: flex;
                flex-direction: row;
                gap: var(--spacing-lg);
                align-items: center;

                & .nav-button {
                    height: var(--font-size-2xl);
                    width: var(--font-size-2xl);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 0;
                }
            }
        }
    }
</style>
