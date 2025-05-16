<script lang="ts">
    import { moveTo } from "../Toolbox/Operations/MoveTo.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        groupedUidSelection: GroupedUidSelection;
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
        children: Snippet
    }

    let {
        groupedUidSelection = $bindable(),
        sourceFolder,
        destinationFolder,
        children
    }: Props = $props();

    const moveEmailsOnClick = async () => {
        await moveTo(
            groupedUidSelection,
            sourceFolder,
            destinationFolder,
        );
    };
</script>

<Context.Item onclick={moveEmailsOnClick}>
    {@render children()}
</Context.Item>
