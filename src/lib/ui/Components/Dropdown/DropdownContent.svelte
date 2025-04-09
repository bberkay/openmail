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
            position: absolute;
            display: flex;
            background-color: var(--color-border-subtle);
            color: var(--color-text-primary);
            flex-direction: column;
            padding: 1px;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            right: -80px;
            top: 30px;
            width: 100px;
        }
    }
</style>
