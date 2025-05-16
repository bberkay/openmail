<script lang="ts">
    import { unsubscribe } from "../Toolbox/Operations/Unsubscribe.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
    }

    let { children }: Props = $props();
</script>

<Context.Item onclick={unsubscribe}>
    {@render children()}
</Context.Item>
