<script lang="ts">
    import { combine } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        value: string;
        content: string;
        icon?: string;
        pinned?: boolean;
        [attribute: string]: unknown;
    }

    let {
        value,
        content,
        icon,
        pinned = false,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<div
    data-value={value}
    data-pinned={pinned}
    class={combine("option", additionalClass)}
    {...restAttributes}
>
    {#if icon}
        <Icon name={icon}/>
    {/if}
    {@html content}
</div>

<style>
    :global {
        .option {
            padding: var(--spacing-xs) var(--spacing-sm);
            cursor: pointer;
            transition: var(--transition-fast);
            color: var(--color-text-secondary);

            &:has(svg) {
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: var(--spacing-sm);
            }

            &:hover{
                background-color: var(--color-hover);
            }

            &.selected {
                background-color: var(--color-border-subtle);
                color: var(--color-text-primary);
            }

            &:has(.dropdown-container) {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
        }
    }
</style>
