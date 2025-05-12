<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { combine } from "$lib/utils";
    import { close, type Props } from "./index";
    import * as Button from "$lib/ui/Components/Button";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    const TOAST_SHOW_DELAY_MS = 10;
    const TOAST_AUTO_CLOSE_DELAY_MS = 3000;

    interface PropsWithMountId extends Props {
        id: string;
    }

    let {
        id,
        content,
        onUndo,
        autoCloseDelay,
        ...attributes
    }: PropsWithMountId = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    let toast: HTMLElement;
    onMount(() => {
        autoCloseDelay = autoCloseDelay || TOAST_AUTO_CLOSE_DELAY_MS;
        setTimeout(() => toast.classList.add("show"), TOAST_SHOW_DELAY_MS);

        const timeout = setTimeout(() => {
            dismiss();
        }, autoCloseDelay);

        toast.dataset.timeout = timeout.toString();
    });

    onDestroy(() => {
        dismiss();
    });

    function dismiss() {
        clearTimeout(Number(toast.dataset.timeout));
        toast.classList.remove("show");
        toast.addEventListener("transitionend", () => {
            close(id);
        });
    }

    const onUndoWrapper = async (e: Event) => {
        if(onUndo) await onUndo(e);
        dismiss();
    }
</script>

<div
    bind:this={toast}
    class={combine("toast", additionalClass)}
    {...restAttributes}
>
    <div>{@html content}</div>
    {#if onUndo}
        <Button.Action
            type="button"
            class="toast-close"
            onclick={onUndoWrapper}
        >
            {local.undo[DEFAULT_LANGUAGE]}
        </Button.Action>
    {/if}
    <Button.Basic
        type="button"
        class="toast-close"
        onclick={dismiss}
    >
        X
    </Button.Basic>
</div>

<style>
    :global {
        .toast{
            width: 400px;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            height: 75px;
            background-color: var(--color-bg-primary);
            padding: var(--spacing-2xs) var(--spacing-md);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            z-index: var(--z-index-toast);

            & .toast-header, .toast-footer {
                display: flex;
                align-items: center;
                justify-content: center;

                & svg {
                    fill: var(--color-bg-primary);
                    height: var(--font-size-lg);
                    width: var(--font-size-lg);
                }
            }

            & .toast-body {
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                margin-left: -10px;

                & .toast-title {
                    color: var(--color-text-primary);
                }
            }

            & .toast-footer {
                display: flex;
                flex-direction: row;
                gap: var(--spacing-2xs);

                & button {
                    padding: var(--spacing-xs) var(--spacing-sm);
                    width: auto;
                }
            }
        }
    }
</style>
