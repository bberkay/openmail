<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>));
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        onclick,
        children,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    const onClickWrapper = async (e: Event) => {
        await onclick(e);
    };
</script>

<div
    class={combine("context-menu-item", additionalClass)}
    {...restAttributes}
>
    <Button.Action
        type="button"
        class="btn-inline"
        style="width: 100%"
        onclick={onClickWrapper}
    >
        {@render children()}
    </Button.Action>
</div>

<style>
    :global {
        .context-menu-item {
            padding: 0 var(--spacing-2xs);

            & .btn-inline {
                justify-content: start;
            }
        }
    }
</style>
