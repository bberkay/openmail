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
    {@render children()}
</div>
