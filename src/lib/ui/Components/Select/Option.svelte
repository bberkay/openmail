<script lang="ts">
    import type { Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        value: string;
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        value,
        children,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    data-value={value}
    class={combine("option", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .option {
            padding: var(--spacing-xs) var(--spacing-sm);
            cursor: pointer;
            transition: background-color var(--transition-fast) var(--ease-default);
            color: var(--color-text-secondary);

            &:hover{
                background-color: var(--color-hover);
            }

            &.selected {
                background-color: var(--color-border);
                color: var(--color-text-primary);
            }

            &:has(.dropdown-container) {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
        }
    }
</style>
