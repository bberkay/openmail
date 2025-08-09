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

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
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

            &:hover:not(:has(.th)):not(:has(.disabled)) {
                background-color: var(--color-hover);
            }
        }
    }
</style>
