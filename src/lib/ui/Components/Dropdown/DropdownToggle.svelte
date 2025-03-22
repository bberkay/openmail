<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props = $props();
</script>

<div {...attributes}>
    <span style="display:none;">#dt#</span>
    {@render children()}
</div>
