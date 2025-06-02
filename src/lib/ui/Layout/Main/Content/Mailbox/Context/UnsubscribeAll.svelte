<script lang="ts">
    import { unsubscribeAll } from "../Toolbox/Operations/UnsubscribeAll.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet;
    }

    let {
        children,
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const unsubscribeAllOnClick = async () => {
        await unsubscribeAll(
            mailboxContext.getGroupedUidSelection()
        );
    }
</script>

<Context.Item onclick={unsubscribeAllOnClick}>
    {@render children()}
</Context.Item>
