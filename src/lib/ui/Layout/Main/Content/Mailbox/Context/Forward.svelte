<script lang="ts">
    import { forward } from "../Toolbox/Operations/Forward.svelte";
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

    const forwardOnClick = async () => {
        await forward(
            mailboxContext.emailSelection.value,
            mailboxContext.getGroupedUidSelection()
        );
        mailboxContext.emailSelection.value = [];
    }
</script>

<Context.Item onclick={forwardOnClick}>
    {@render children()}
</Context.Item>
