<script lang="ts">
    import { combine } from "$lib/utils";
    import { type Snippet } from "svelte";

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

<span
    class={combine("badge", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</span>

<style>
    :global {
        .badge {
            padding: var(--spacing-xs);
            padding-top: calc(var(--spacing-2xs) / 2);
            padding-bottom: var(--spacing-2xs);
            border-radius: var(--radius-sm);
            border: 1px solid var(--color-border);
            background-color: transparent;
            color: var(--color-text-primary);
        }
    }
</style>
