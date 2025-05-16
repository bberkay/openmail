<script lang="ts">
    import { deleteFrom } from "../Toolbox/Operations/DeleteFrom.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        groupedUidSelection: GroupedUidSelection;
        folder: string | Folder;
        children: Snippet;
        currentOffset?: number;
    }

    let {
        groupedUidSelection = $bindable(),
        folder,
        children,
        currentOffset = $bindable()
    }: Props = $props();

    const deleteEmailsOnClick = async () => {
        await deleteFrom(
            groupedUidSelection,
            folder,
            false,
            currentOffset
        );
    };
</script>

<Context.Item onclick={deleteEmailsOnClick}>
    {@render children()}
</Context.Item>
