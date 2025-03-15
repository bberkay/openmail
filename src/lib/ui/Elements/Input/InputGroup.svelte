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
        `input-group-${direction}`,
        additionalClass
    )}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .input-group-vertical {
            display: flex;
            flex-direction: column;
            text-align: left;
            margin-bottom: var(--spacing-xs);
        }

        .input-group-horizontal {
            display: flex;
            align-items: center;
            gap: var(--spacing-lg);

            & input[type="checkbox"] + label {
                margin-top: 7px;
            }
        }
    }
</style>
