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

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
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

            &.form-group-vertical {
                flex-direction: column;
                text-align: left;
                margin-bottom: var(--spacing-xs);
            }

            &.form-group-horizontal {
                flex-direction: row;
                align-items: center;
                gap: var(--spacing-lg);

                & input[type="checkbox"] + label {
                    margin-top: 7px;
                }
            }
        }
    }
</style>
