<script lang="ts">
    import { unsubscribe } from "../Toolbox/Operations/Unsubscribe.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "../../Mailbox";

    interface Props {
        children: Snippet;
    }

    let {
        children,
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const unsubscribeOnClick = async () => {
        await unsubscribe(
            mailboxContext.emailSelection.value,
            mailboxContext.getGroupedUidSelection()
        );
        mailboxContext.emailSelection.value = [];
    }
</script>

<Context.Item onclick={unsubscribeOnClick}>
    {@render children()}
</Context.Item>
