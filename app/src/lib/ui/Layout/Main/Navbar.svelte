<script lang="ts">
    import Folders from "$lib/ui/Layout/Main/Navbar/Folders.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import Search from "$lib/ui/Layout/Main/Navbar/Search.svelte";
    import Notifications from "$lib/ui/Layout/Main/Navbar/Notifications.svelte";
    import Compose from "$lib/ui/Layout/Main/Navbar/Compose.svelte";
</script>

<nav>
    <div class="nav-section">
        <!--<h1 class="app-title">Openmail</h1>-->
        <Folders />
    </div>
    <div class="nav-section">
        <Search />
    </div>
    <div class="nav-section">
        <Compose />
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
            align-items: stretch;
            width: 100%;

            & .app-title {
                font-family: 'Inter', sans-serif;
                font-size: var(--font-size-xl);
                font-weight: var(--font-weight-bold);
                color: var(--color-text-primary);
            }

            & .nav-section {
                display: flex;
                flex-direction: row;
                gap: var(--spacing-xs);
            }
        }
    }
</style>
