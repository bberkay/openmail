<script lang="ts">
    import * as Input from "$lib/ui/Components/Input";

    interface Props {
        checked?: boolean;
        element?: HTMLInputElement;
        [attribute: string]: unknown;
    }

    let {
        checked = $bindable(),
        element,
        ...attributes
    }: Props = $props();
</script>

<label class="switch">
    <Input.Basic
        bind:element
        bind:checked
        {...attributes}
    />
    <span class="slider"></span>
</label>

<style>
    :global {
        .switch {
            position: relative;
            display: inline-block;
            width: var(--font-size-2xl);
            height: calc(var(--font-size-2xl) / 1.75);

            & input {
                opacity: 0;
                width: 0;
                height: 0;
            }

            & input:checked + .slider {
                background-color: var(--color-checked);
            }

            & input:checked + .slider:before {
                -webkit-transform: translateX(calc(var(--font-size-2xl) - calc(var(--font-size-2xl) / 1.75)));
                -ms-transform: translateX(calc(var(--font-size-2xl) - calc(var(--font-size-2xl) / 1.75)));
                transform: translateX(calc(var(--font-size-2xl) - calc(var(--font-size-2xl) / 1.75)));
            }

            & .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: var(--color-gray);
                -webkit-transition: var(--transition-slow);
                transition: var(--transition-slow);
                border-radius: calc(var(--font-size-2xl) / 1.75);

                &:before {
                    position: absolute;
                    content: "";
                    height: calc(var(--font-size-2xl) - calc(var(--font-size-2xl) / 1.75));
                    height: calc(var(--font-size-2xl) - calc(var(--font-size-2xl) / 1.75));
                    left: var(--spacing-2xs);
                    bottom: var(--spacing-2xs);
                    background-color: white;
                    -webkit-transition: var(--transition-slow);
                    transition: var(--transition-slow);
                    border-radius: 50%;
                }
            }
        }
    }
</style>
