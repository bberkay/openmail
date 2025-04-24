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

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
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
            padding: var(--spacing-xs) var(--spacing-md);
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all var(--transition-fast) var(--ease-default);
            font-size: var(--font-size-sm);
            display: flex;
            align-items: center;
            justify-content: center;

            &[disabled], &.disabled {
                cursor:not-allowed!important;
                opacity: 0.7!important;
            }

            &:hover {
                opacity: 0.9;
            }

            &:active {
                opacity: 0.7;
            }

            &:has(svg) {
                justify-content: space-between;
            }

            &.btn-cta {
                width: 100%;
                font-weight: var(--font-weight-bold);
                background-color: var(--color-text-primary);
                color: var(--color-bg-primary);
            }

            &.btn-inline {
                padding: 0;
                margin: 0;
                background-color: transparent;
                color: var(--color-text-primary);
            }

            &.btn-outline {
                background-color: transparent;
                color: var(--color-text-primary);
                border: 1px solid var(--color-border);

                &:hover {
                    background-color: var(--color-hover);
                }

                &:active {
                    background-color: var(--color-border);
                }
            }
        }
    }
</style>
