<script lang="ts">
    import { combine } from "$lib/utils";
    import type { Snippet } from "svelte";

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

<div
    role="button"
    tabindex="0"
    class={combine("popover-toggle", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>
