<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        [attribute: string]: unknown;
    }

    let {
        children,
        onclick,
        ...attributes
    }: Props = $props();
</script>

<button {...attributes} type="button" onclick={onclick}>
    {@render children()}
</button>
