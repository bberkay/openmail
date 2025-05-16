<script lang="ts">
    import { reply } from "../Toolbox/Operations/Reply.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
    }

    let { children }: Props = $props();
</script>

<Context.Item onclick={reply}>
    {@render children()}
</Context.Item>
