<script lang="ts">
    import Folders from "$lib/ui/Layout/Main/Navbar/Folders.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import Search from "$lib/ui/Layout/Main/Navbar/Search.svelte";
    import Notifications from "$lib/ui/Layout/Main/Navbar/Notifications.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Navbar/Compose.svelte";
</script>

<nav>
    <div class="nav-section">
        <Folders />
        <Search />
    </div>
    <div class="nav-section">
        <Compose />
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
            }
        }
    }
</style>
