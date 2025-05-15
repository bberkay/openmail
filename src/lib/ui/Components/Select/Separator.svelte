<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        [attribute: string]: unknown;
    }

    let {
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
></div>

<style>
    :global {
        .custom-select-wrapper .options-list {
            .separator + .separator {
                display: none;
            }
        }
    }
</style>
