<script lang="ts">
    import { moveTo } from "../Toolbox/Operations/MoveTo.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
    }

    let {
        children,
        sourceFolder,
        destinationFolder,
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const moveEmailsOnClick = async () => {
        await moveTo(
            sourceFolder,
            destinationFolder,
            mailboxContext.getGroupedUidSelection(),
            mailboxContext.currentOffset.value
        );
    };
</script>

<Context.Item onclick={moveEmailsOnClick}>
    {@render children()}
</Context.Item>
