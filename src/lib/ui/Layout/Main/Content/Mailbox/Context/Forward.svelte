<script lang="ts">
    import { forward } from "../Toolbox/Operations/Forward.svelte";
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

    const forwardOnClick = async () => {
        await forward(
            emailSelection,
            groupedUidSelection
        );
    }
</script>

<Context.Item onclick={forwardOnClick}>
    {@render children()}
</Context.Item>
