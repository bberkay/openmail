<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        title?: string;
        [attribute: string]: unknown;
    }

    let {
        title,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<div
    role="separator"
    class={combine("separator", additionalClass)}
    {...restAttributes}
>
    {#if title}
        <div class="separator-title">{title}</div>
    {/if}
</div>

<style>
    :global {
        .dropdown-container {
            .separator + .separator {
                display: none;
            }
        }
    }
</style>
