<script lang="ts">
    import Operations from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/Operations.svelte";
    import Pagination from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/Pagination.svelte";
    import type { EmailSelection, GroupedUidSelection } from "../Mailbox.svelte";

    interface Props {
        groupedUidSelection: GroupedUidSelection;
        emailSelection: EmailSelection;
        currentOffset: number;
    }

    let {
        groupedUidSelection = $bindable(),
        emailSelection = $bindable(),
        currentOffset = $bindable()
    }: Props = $props();

</script>

<div class="toolbox">
    <Operations
        bind:groupedUidSelection
        bind:emailSelection
        bind:currentOffset
    />
    <Pagination bind:currentOffset />
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
