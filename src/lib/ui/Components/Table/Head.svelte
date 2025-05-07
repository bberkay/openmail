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

<th
    class={combine("th", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</th>

<style>
    :global {
        .th{
            padding: var(--spacing-xs) var(--spacing-xs);
            font-size: var(--font-size-sm);
            border-bottom: 1px solid var(--color-border);
            font-weight: bold;
            color: var(--color-text-secondary);
        }
    }
</style>
