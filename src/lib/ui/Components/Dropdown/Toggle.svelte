<script lang="ts">
    import { combine } from "$lib/utils";
    import type { Snippet } from "svelte";
    import Icon from "$lib/ui/Components/Icon";
    import { show as showTooltip } from "$lib/ui/Components/Tooltip";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        tooltip,
        ...restAttributes
    } = attributes;
</script>

<div
    role="button"
    tabindex="0"
    class={combine("dropdown-toggle", additionalClass)}
    {...restAttributes}
>
    <div class="dropdown-toggle-content">
        {@render children()}
    </div>
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
            gap: var(--spacing-2xs);

            & .dropdown-toggle-content {
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
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
