<script lang="ts">
    import { combine } from "$lib/utils";
    import Icon from "$lib/ui/Elements/Icon";
    import { close } from "./index";
    import * as Button from "$lib/ui/Elements/Button";

    interface Props {
        content: string;
        lefticon?: Icon;
        righticon?: Icon;
        removeable?: boolean;
        [attribute: string]: unknown;
    }

    let {
        content,
        lefticon,
        righticon,
        removeable,
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
    {#if removeable}
        <Button.Basic
            type="button"
            class="inline"
            onclick={close}
        >X</Button.Basic>
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
