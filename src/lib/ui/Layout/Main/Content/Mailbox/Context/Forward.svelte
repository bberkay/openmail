<script lang="ts">
    import { forward } from "../Toolbox/Operations/Forward.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
    }

    let { children }: Props = $props();
</script>

<Context.Item onclick={forward}>
    {@render children()}
</Context.Item>
