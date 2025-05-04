<script lang="ts">
    import type { Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    class={combine("dropdown-content hidden", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .dropdown-content {
            width: 100%;
            position: absolute;
            display: flex;
            user-select: none;
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            flex-direction: column;
            text-align: left!important;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            z-index: var(--z-index-dropdown);
        }

        .dropdown-container.inline {
            & .dropdown-content {
                width: max-content;
            }
        }
    }
</style>
