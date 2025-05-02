<script lang="ts">
    import Folders from "$lib/ui/Layout/Main/Navbar/Folders.svelte";
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import Search from "$lib/ui/Layout/Main/Navbar/Search.svelte";
    import Notifications from "$lib/ui/Layout/Main/Navbar/Notifications.svelte";
    import Compose from "$lib/ui/Layout/Main/Navbar/Compose.svelte";
</script>

<nav>
    <div class="nav-section">
        <Folders />
        <Search />
    </div>
    <div class="nav-section">
        <h1 class="logo">Openmail</h1>
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
            align-items: flex-start;
            width: 100%;
            padding: var(--spacing-lg);
            font-size: var(--font-size-xs);

            & .nav-section {
                display: flex;
                flex-direction: row;
                gap: var(--spacing-xs);

                & .logo {
                    font-size: var(--font-size-2xl);
                }
            }
        }
    }
</style>
