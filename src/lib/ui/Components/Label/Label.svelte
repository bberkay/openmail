<script lang="ts">
    import { combine } from "$lib/utils";
    import { type Snippet } from "svelte";

    interface Props {
        children: Snippet
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<label
    class={combine("label", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</label>

<style>
    :global {
        .label{
            text-align: left;
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
            margin-bottom: var(--spacing-2xs);
            margin-left: calc(var(--spacing-2xs) / 2);

            &.label-sm {
                font-size: var(--font-size-xs);
            }
        }
    }
</style>
