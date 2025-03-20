<script lang="ts">
    import { combine } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        content: string;
        lefticon?: Icon;
        righticon?: Icon;
        [attribute: string]: unknown;
    }

    let {
        content,
        lefticon,
        righticon,
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    class={combine("badge", additionalClass)}
    {...restAttributes}
>
    {#if lefticon}
        {lefticon}
    {/if}
    <span>
        {@html content}
    </span>
    {#if righticon}
        {righticon}
    {/if}
</div>

<style>
    :global {
        .badge {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-xs);
            padding-top: calc(var(--spacing-2xs) / 2);
            padding-bottom: var(--spacing-2xs);
            border-radius: var(--radius-sm);
            border: 1px solid var(--color-border);
            background-color: transparent;
            color: var(--color-text-primary);
        }
    }
</style>
