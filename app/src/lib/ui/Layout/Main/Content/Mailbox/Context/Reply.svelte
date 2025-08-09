<script lang="ts">
    import { reply } from "../Toolbox/Operations/Reply.svelte";
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

    const replyOnClick = async () => {
        await reply(
            mailboxContext.emailSelection.value,
            mailboxContext.getGroupedUidSelection()
        );
        mailboxContext.emailSelection.value = [];
    }
</script>

<Context.Item onclick={replyOnClick}>
    {@render children()}
</Context.Item>
