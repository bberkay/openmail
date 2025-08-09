<script lang="ts">
    import { combine } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        content: string;
        lefticon?: string;
        righticon?: string;
        onclick?: (e: Event) => void;
        [attribute: string]: unknown;
    }

    let {
        content,
        lefticon,
        righticon,
        onclick,
        ...attributes
    }: Props  = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<div
    class={combine(`badge ${onclick ? "clickable" : ""}`, additionalClass)}
    {onclick}
    {...restAttributes}
>
    {#if lefticon}
        <Icon name={lefticon} />
    {/if}
    <span>
        {@html content}
    </span>
    {#if righticon}
        <Icon name={righticon} />
    {/if}
</div>

<style>
    :global {
        .badge {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            gap: var(--spacing-xs);
            padding: var(--spacing-xs);
            padding-top: calc(var(--spacing-2xs) / 2);
            padding-bottom: var(--spacing-2xs);
            border-radius: var(--radius-sm);
            border: 1px solid var(--color-border);
            background-color: transparent;
            color: var(--color-text-primary);
            margin-top: var(--spacing-2xs);
            font-size: var(--font-size-xs);

            & svg {
                width: var(--font-size-sm);
                height: var(--font-size-sm);
            }

            &.clickable {
                cursor: pointer;
            }

            &.clickable:hover {
                background-color: var(--color-hover);
            }

            &.clickable:active {
                background-color: var(--color-border);
            }
        }
    }
</style>
