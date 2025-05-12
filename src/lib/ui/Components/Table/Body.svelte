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

<tbody
    class={combine("tbody", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</tbody>

<style>
    :global {
        .tbody{
            opacity: 1; /* temporary for prevent empty ruleset warning */
        }
    }
</style>
