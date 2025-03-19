<script lang="ts">
    import Account from "$lib/ui/Layout/Main/Navbar/Account.svelte";
    import SearchBar from "$lib/ui/Layout/Main/Navbar/SearchBar.svelte";

    let navbar: HTMLElement;
</script>

<nav bind:this={navbar}>
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
            }
        }
    }
</style>
