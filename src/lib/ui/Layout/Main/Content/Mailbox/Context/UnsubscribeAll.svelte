<script lang="ts">
    import { unsubscribeAll } from "../Toolbox/Operations/UnsubscribeAll.svelte";
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

    const unsubscribeAllOnClick = async () => {
        await unsubscribeAll(
            emailSelection,
            groupedUidSelection
        );
    }
</script>

<Context.Item onclick={unsubscribeAllOnClick}>
    {@render children()}
</Context.Item>
