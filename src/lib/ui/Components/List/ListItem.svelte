<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        onclick?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        type?: "disabled" | "active";
        [attribute: string]: unknown;
    }

    let {
        children,
        onclick,
        type,
        ...attributes
    }: Props = $props();

    const onClickWrapper = async (e: Event) => {
        if(onclick && type !== "disabled") await onclick(e);
    }
</script>

<li
    class="list-item {type} {onclick ? "clickable": ""}"
    onclick={onClickWrapper}
    {...attributes}
>
    {@render children()}
</li>

<style>
    :global {
        .list-container {
            .list-item {
                position: relative;
                display: block;
                padding: var(--spacing-sm);
                background-color: var(--color-bg-primary);
                border-bottom: 1px solid var(--color-border);
                text-decoration: none;
                color: var(--color-text-primary);
                transition: all var(--transition-fast) var(--ease-default);

                &:first-child {
                    border-top-left-radius: var(--radius-sm);
                    border-top-right-radius: var(--radius-sm);
                }

                &:hover {
                    background-color: var(--color-hover);
                    border-color: var(--color-text-primary);
                }

                &.clickable:active{
                    background-color: var(--color-border);
                }

                &.clickable {
                    cursor: pointer;
                }

                &.active {
                    background-color: var(--color-hover);
                    border-color: var(--color-text-primary);
                }
            }
        }
    }
</style>
