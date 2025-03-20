<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<table
    class={combine("table", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</table>

<style>
    :global {
        .table {
            width: 100%;
            border-spacing: 0;
            border-radius: var(--radius-sm);
        }
    }
</style>
