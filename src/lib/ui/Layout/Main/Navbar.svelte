<script lang="ts">
    import Folders from "$lib/ui/Layout/Main/Navbar/Folders.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import Search from "$lib/ui/Layout/Main/Navbar/Search.svelte";
    import Notifications from "$lib/ui/Layout/Main/Navbar/Notifications.svelte";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    const showCompose = () => {
        showContent(Compose);
    }
</script>

<nav>
    <div class="nav-section">
        <Folders />
        <Search />
    </div>
    <div class="nav-section">
        <Button.Basic
            type="button"
            class="btn-cta nav-button compose-button"
            style="width:auto"
            onclick={showCompose}
        >
            <Icon name="compose" style="fill:var(--color-bg-primary)"/>
            Compose
        </Button.Basic>
        <Account />
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
            font-size: var(--font-size-xs);

            & .nav-section {
                display: flex;
                flex-direction: row;
                gap: var(--spacing-xs);

                & .nav-button {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: var(--spacing-2xs);
                    padding-left: var(--spacing-sm);
                }

                & .folders {
                    width: 120px;
                }

                & .account {
                    width: 200px;
                }
            }
        }
    }
</style>
