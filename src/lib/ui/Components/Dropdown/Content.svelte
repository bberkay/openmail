<script lang="ts">
    import type { Snippet } from "svelte";
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

<div
    class={combine("dropdown-content hidden", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .dropdown-content {
            width: max-content;
            position: absolute;
            user-select: none;
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            text-align: left!important;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            z-index: var(--z-index-dropdown);
        }

        .dropdown-container {
            & .dropdown-content {
                width: 100%;
            }
        }
    }
</style>
