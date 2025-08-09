<script lang="ts">
    import Operations from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/Operations.svelte";
    import Pagination from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/Pagination.svelte";
</script>

<div class="toolbox">
    <Operations />
    <Pagination />
</div>

<style>
    :global {
        .toolbox {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            width: 80%;
            padding: var(--spacing-sm) var(--spacing-md);
            height: 60px;
        }
    }
</style>
