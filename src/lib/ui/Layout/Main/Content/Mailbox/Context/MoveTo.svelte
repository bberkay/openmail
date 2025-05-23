<script lang="ts">
    import { moveTo } from "../Toolbox/Operations/MoveTo.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
        groupedUidSelection: GroupedUidSelection;
        currentOffset?: number;
    }

    let {
        children,
        sourceFolder,
        destinationFolder,
        groupedUidSelection = $bindable(),
        currentOffset = $bindable()
    }: Props = $props();

    const moveEmailsOnClick = async () => {
        await moveTo(
            sourceFolder,
            destinationFolder,
            groupedUidSelection,
            currentOffset
        );
    };
</script>

<Context.Item onclick={moveEmailsOnClick}>
    {@render children()}
</Context.Item>
