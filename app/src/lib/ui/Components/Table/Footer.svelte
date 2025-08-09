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

<tfoot
    class={combine("tfoot", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</tfoot>

<style>
    :global {
        .tfoot{
            opacity: 1; /* temporary for prevent empty ruleset warning */
        }
    }
</style>
