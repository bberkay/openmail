<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        [attribute: string]: unknown;
    }

    let {
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<input
    class={combine("input", additionalClass)}
    {...restAttributes}
/>

<style>
    :global{
        .input{
            width: 100%;
            padding: var(--spacing-sm) var(--spacing-2xs);
            border: none;
            border-bottom: 1px solid var(--color-border);
            background-color: transparent;
            color: var(--color-text-primary);
            transition: all var(--transition-fast) var(--ease-default);

            &:focus {
                outline: none;
                border-color: var(--color-text-primary);
            }

            &:disabled {
                border-bottom: none;
            }
        }

        .input[type="checkbox"]{
            padding: 0;
            appearance: none;
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: var(--radius-sm);
            background-color: transparent;
            border: 1px solid var(--color-border);
            cursor: pointer;
            position: relative;

            &:checked {
                background-color: var(--color-text-primary);

                &::after {
                    content: "";
                    position: absolute;
                    top: 2px;
                    left: 5px;
                    width: 3px;
                    height: 8px;
                    border: solid var(--color-bg-primary);
                    border-width: 0 2px 2px 0;
                    transform: rotate(45deg);
                }
            }
        }

        .input + .muted{
            margin-left: calc(var(--spacing-2xs) / 2);
            margin-top: var(--spacing-xs);
        }
    }
</style>
