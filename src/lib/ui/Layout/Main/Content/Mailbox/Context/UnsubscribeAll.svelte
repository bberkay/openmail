<script lang="ts">
    import { unsubscribeAll } from "../Toolbox/Operations/UnsubscribeAll.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
    }

    let { children }: Props = $props();
</script>

<Context.Item onclick={unsubscribeAll}>
    {@render children()}
</Context.Item>
