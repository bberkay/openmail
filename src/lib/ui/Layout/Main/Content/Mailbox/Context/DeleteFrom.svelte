<script lang="ts">
    import { deleteFrom } from "../Toolbox/Operations/DeleteFrom.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "../../Mailbox";

    interface Props {
        children: Snippet;
        folder: string | Folder;
    }

    let {
        children,
        folder,
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const deleteEmailsOnClick = async () => {
        await deleteFrom(
            folder,
            mailboxContext.getGroupedUidSelection(),
            mailboxContext.currentOffset.value,
        );
        mailboxContext.emailSelection.value = [];
    };
</script>

<Context.Item onclick={deleteEmailsOnClick}>
    {@render children()}
</Context.Item>
