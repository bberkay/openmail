<script lang="ts">
    import { onMount, type Snippet } from "svelte";
    import { combine, createDomElement } from "$lib/utils";

    interface Props {
        children: Snippet
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

    let wrapper: HTMLElement;
    onMount(() => {
        const preInput = createDomElement('<div class="pre-input"></div>');
        const postInput = createDomElement('<div class="post-input"></div>');

        let inputFound = false;
        Array.from(wrapper.children).forEach((child) => {
            if (child.tagName == "INPUT") {
                inputFound = true;
                return
            }

            if (child.tagName == "BUTTON") {
                if (!child.classList.contains("btn-inline")){
                    child.classList.add("btn-inline");
                }
            }

            if (!inputFound) {
                preInput.append(child);
            } else {
                postInput.append(child);
            }
        });

        wrapper.prepend(preInput);
        wrapper.append(postInput);
    })
</script>

<div
    bind:this={wrapper}
    class={combine("input-group", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .input-group{
            display: flex;
            align-items: center;
            transition: all var(--transition-fast) var(--ease-default);
            border-bottom: 1px solid var(--color-border);

            & input {
                border: none !important;
                flex-grow: 1;
            }

            &:has(input:focus) {
                border-color: var(--color-text-primary);

                & svg {
                    fill: var(--color-text-primary)!important;
                }
            }

            & .pre-input,
            & .post-input {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: center;
                gap: 10px;
                cursor: pointer;
                color: var(--color-text-secondary);
                background: transparent;
                border: none;
                transition: all var(--transition-fast) var(--ease-default);

                & svg {
                    width: var(--font-size-lg);
                    height: var(--font-size-lg);
                }
            }

            & .pre-input:has(svg) + input,
            & input + .post-input:has(svg) {
                margin-left: var(--spacing-2xs);
            }
        }
    }
</style>
