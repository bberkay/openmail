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

<tr
    class={combine("tr", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</tr>

<style>
    :global {
        .tr {
            transition: background-color var(--transition-fast) var(--ease-default);
            cursor: pointer;

            &:hover:not(:has(.th)) {
                background-color: var(--color-hover);
            }
        }
    }
</style>
