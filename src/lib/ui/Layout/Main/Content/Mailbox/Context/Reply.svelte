<script lang="ts">
    import { reply } from "../Toolbox/Operations/Reply.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";
    import type { EmailSelection, GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet;
        groupedUidSelection: GroupedUidSelection;
        emailSelection: EmailSelection
    }

    let {
        children,
        groupedUidSelection = $bindable(),
        emailSelection = $bindable(),
    }: Props = $props();

    const replyOnClick = async () => {
        await reply(
            emailSelection,
            groupedUidSelection
        );
    }
</script>

<Context.Item onclick={replyOnClick}>
    {@render children()}
</Context.Item>
