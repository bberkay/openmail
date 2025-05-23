<script lang="ts">
    import { deleteFrom } from "../Toolbox/Operations/DeleteFrom.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet;
        folder: string | Folder;
        groupedUidSelection: GroupedUidSelection;
        currentOffset?: number;
    }

    let {
        children,
        folder,
        groupedUidSelection,
        currentOffset
    }: Props = $props();

    const deleteEmailsOnClick = async () => {
        await deleteFrom(
            folder,
            groupedUidSelection,
            currentOffset,
        );
    };
</script>

<Context.Item onclick={deleteEmailsOnClick}>
    {@render children()}
</Context.Item>
