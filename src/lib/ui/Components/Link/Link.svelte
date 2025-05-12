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

<a
    class={combine("link", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</a>

<style>
    :global {
        .link{
            color: var(--color-link);
            transition: opacity var(--transition-fast) var(--ease-default);

            &:hover {
                opacity: 0.8;
            }
        }
    }
</style>
