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

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<label
    class={combine("label", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</label>

<style>
    :global {
        .label{
            text-align: left;
            font-size: var(--font-size-sm);
            color: var(--color-text-primary);
            margin-left: calc(var(--spacing-2xs) / 2);
        }
    }
</style>
