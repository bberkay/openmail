<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<ul
    class={combine("list-container", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</ul>


<style>
    :global {
        .list-container {
            display: flex;
            flex-direction: column;
            padding-left: 0;
            overflow: hidden;
            font-size: var(--font-size-sm);
        }
    }
</style>
