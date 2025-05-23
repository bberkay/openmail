<script lang="ts">
    import { unsubscribe } from "../Toolbox/Operations/Unsubscribe.svelte";
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
        groupedUidSelection,
        emailSelection,
    }: Props = $props();

    const unsubscribeOnClick = async () => {
        await unsubscribe(
            emailSelection,
            groupedUidSelection
        );
    }
</script>

<Context.Item onclick={unsubscribeOnClick}>
    {@render children()}
</Context.Item>
