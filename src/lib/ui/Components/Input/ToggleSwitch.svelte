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
    <input type="checkbox" />
    <span class="slider"></span>
</label>

<style>
    :global {
        .switch {
            position: relative;
            display: inline-block;
            width: 35px;
            height: 20px;

            & input {
                opacity: 0;
                width: 0;
                height: 0;
            }

            & input:checked + .slider {
                background-color: var(--color-checked);
            }

            & input:checked + .slider:before {
                -webkit-transform: translateX(14px);
                -ms-transform: translateX(14px);
                transform: translateX(14px);
            }

            & .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: var(--color-gray);
                -webkit-transition: var(--transition-normal);
                transition: var(--transition-normal);
                border-radius: 10px;

                &:before {
                    position: absolute;
                    content: "";
                    height: 14px;
                    width: 14px;
                    left: 4px;
                    bottom: 3px;
                    background-color: white;
                    -webkit-transition: var(--transition-normal);
                    transition: var(--transition-normal);
                    border-radius: 50%;
                }
            }
        }
    }
</style>
