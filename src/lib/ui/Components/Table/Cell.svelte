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

<td
    class={combine("td", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</td>

<style>
    :global {
        .td {
            padding: var(--spacing-xs) var(--spacing-xs);
            font-size: var(--font-size-sm);
            border-bottom: 1px solid var(--color-border);

            &.full {
                text-align: center;
            }
        }
    }
</style>
