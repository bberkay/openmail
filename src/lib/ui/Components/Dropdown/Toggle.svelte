<script lang="ts">
    import { combine } from "$lib/utils";
    import type { Snippet } from "svelte";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    role="button"
    tabindex="0"
    class={combine("dropdown-toggle", additionalClass)}
    {...restAttributes}
>
    {@render children()}
    <Icon name="dropdown" class="non-inline-dropdown-icon"/>
</div>

<style>
    :global {
        .dropdown-toggle {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--color-border);
            border-radius: var(--radius-sm);
            border-bottom-left-radius: none;
            border-bottom-right-radius: none;
            padding: var(--spacing-xs) var(--spacing-sm);
            cursor: pointer;
            background-color: var(--color-bg-primary);
        }

        .dropdown-container.inline {
            & .dropdown-toggle {
                justify-content: center;
                border: 1px solid transparent!important;
                padding: var(--spacing-2xs) var(--spacing-2xs);
                background-color: transparent;

                &:hover {
                    background-color: var(--color-border);
                }
            }

            & .non-inline-dropdown-icon {
                display: none;
            }
        }
    }
</style>
