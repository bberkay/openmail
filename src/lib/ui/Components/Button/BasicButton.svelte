<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props  = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);
</script>

<button
    class={combine("btn", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</button>

<style>
    :global {
        .btn{
            padding: var(--spacing-xs) var(--spacing-sm);
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all var(--transition-fast) var(--ease-default);
            font-size: var(--font-size-sm);
            display: flex;
            align-items: center;
            justify-content: center;

            &:hover,
            &.hover {
                background-color: var(--color-hover);
            }

            &:active,
            &.active {
                background-color: var(--color-border);
            }

            &.btn-cta {
                width: 100%;
                font-weight: var(--font-weight-bold);
                background-color: var(--color-text-primary);
                color: var(--color-bg-primary);
            }

            &.btn-inline {
                padding: var(--spacing-2xs) var(--spacing-sm);
                margin: 0;
                background-color: transparent;
                color: var(--color-text-primary);

                &:has(> svg:only-child) {
                    padding: var(--spacing-2xs) var(--spacing-xs)!important;
                }

                &:hover,
                &.hover {
                    background-color: var(--color-border);

                    & svg {
                        fill: var(--color-text-primary);
                    }
                }

                &:active,
                &.active {
                    background-color: var(--color-border-subtle);
                }
            }

            &.btn-outline {
                background-color: transparent;
                color: var(--color-text-primary);
                border: 1px solid var(--color-border);

                &:hover,
                &.hover {
                    background-color: var(--color-hover);
                }

                &:active,
                &.active {
                    background-color: var(--color-border);
                }
            }

            &:has(svg) {
                justify-content: space-between;

                & svg {
                    margin-right: var(--spacing-xs);
                    margin-left: calc(-0.5 * var(--spacing-xs));
                }

                &:not(:has(span)) svg {
                    margin-right: calc(-0.5 * var(--spacing-xs));
                }
            }

            &.btn-md {
                font-size: var(--font-size-xs);
            }

            &.btn-sm {
                padding: var(--spacing-2xs) var(--spacing-sm)!important;
                font-size: var(--font-size-xs);

                & svg {
                    width: var(--font-size-md);
                    height: var(--font-size-md);
                }
            }
        }
    }
</style>
