<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        direction?: "vertical" | "horizontal"
        children: Snippet
        [attribute: string]: unknown;
    }

    let {
        direction = "vertical",
        children,
        ...attributes
    }: Props  = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<div
    class={combine(
        `form-group form-group-${direction}`,
        additionalClass
    )}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .form-group {
            display: flex;

            &:not(:has(.form-group)):not(:first-of-type) {
                margin-top: var(--spacing-lg);
            }

            & .form-group {
                margin-top: var(--spacing-2xs);
            }

            &.form-group-vertical {
                flex-direction: column;
                text-align: left;
            }

            &.form-group-horizontal {
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                gap: var(--spacing-xl);

                & .form-group {
                    width: 100%;
                }

                &:has(input[type="checkbox"] + label) {
                    justify-content: left;
                    gap: var(--spacing-xs);
                }
            }
        }
    }
</style>
