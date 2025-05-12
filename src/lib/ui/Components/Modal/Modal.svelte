<script lang="ts">
    import { onMount } from "svelte";
    import type { Snippet } from "svelte";
    import { close } from "./index";
    import { combine, createDomElement } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    const DEFAULT_CLOSE_BUTTON_TEMPLATE = `
        <button type="button" class="btn btn-outline" data-modal-close>
            ${local.close[DEFAULT_LANGUAGE]}
        </button>
    `;

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    let modal: HTMLElement;
    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;

        let closeButton = modal.querySelector("button[data-modal-close]");
        if (!closeButton) {
            closeButton = createDomElement(DEFAULT_CLOSE_BUTTON_TEMPLATE);
            modal.appendChild(closeButton);
        }
        closeButton.addEventListener("click", close);
    });
</script>

<div
    bind:this={modal}
    class={combine("modal", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .modal{
            pointer-events: all!important;
            width: var(--container-sm);
            background-color: var(--color-bg-primary);
            padding: var(--spacing-lg) var(--spacing-xl);
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            z-index: var(--z-index-modal);

            &.frameless {
                display: flex;
                flex-direction: column;
                width: var(--container-md);
                padding: 0;

                & .frameless-header {
                    padding: 0 var(--spacing-sm);
                    border-color: transparent!important;
                }

                & .frameless-body {
                    display: flex;
                    flex-direction: column;
                    height: var(--container-md);
                    overflow-y: scroll!important;
                    overflow-x: hidden;
                    z-index: var(--z-index-modal);
                    padding: var(--spacing-md);
                    padding-right: calc(var(--spacing-md) + 5px); /* because of scrollbar */
                    background-color: var(--color-bg-primary);
                    border-bottom-left-radius: var(--radius-lg);
                    border-bottom-right-radius: var(--radius-lg);
                    border-top: 1px solid var(--color-border-subtle);
                }
            }

            & .modal-header {
                color: var(--color-text-primary);
                margin-bottom: var(--spacing-2xs);
                font-weight: var(--font-weight-bold);
                font-size: var(--font-size-xl);
            }

            & .modal-footer {
                display: flex;
                flex-direction: row;
                justify-content: flex-end;
                margin-top: var(--spacing-md);
                gap: var(--spacing-md);
                color: var(--color-text-primary);
            }
        }
    }
</style>
