<script lang="ts">
    import { combine } from "$lib/utils";

    interface Props {
        onchange?: (((checked: boolean) => void) | ((checked: boolean) => Promise<void>)),
        checked?: boolean;
        element?: HTMLInputElement;
        [attribute: string]: unknown;
    }

    let {
        onchange,
        checked = $bindable(),
        element,
        ...attributes
    }: Props = $props();

    checked = checked || false;

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    const onchangeWrapper = async () => {
        if(onchange) await onchange(checked as boolean);
    }
</script>

<label class={combine("switch", additionalClass)}>
    <input
        type="checkbox"
        bind:this={element}
        bind:checked={checked}
        onchange={onchangeWrapper}
        {...restAttributes}
    />
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
