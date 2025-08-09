<script lang="ts">
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { Spinner } from "$lib/ui/Components/Loader";
</script>

<div class="loading-page">
    <h3>
        <Spinner size="medium"/>
        {local.connecting_to_accounts[DEFAULT_LANGUAGE]}
    </h3>
</div>

<style>
    .loading-page {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;

        & h3 {
            display: flex;
            gap: var(--spacing-sm);
        }
    }
</style>
