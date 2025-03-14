<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import type { Snippet } from "svelte";
    import { close } from "./index";

    interface Props {
        id: string;
        content: string;
        autoCloseDelay?: number;
        onUndo?: (e: Event) => void;
    }

    let { id, content, onUndo, autoCloseDelay }: Props = $props();
    let toast: HTMLElement;

    onMount(() => {
        autoCloseDelay = autoCloseDelay || 3000;
        setTimeout(() => toast.classList.add("show"), 10);

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
</script>

<div class="toast" bind:this={toast}>
    <div>{@html content}</div>
    {#if onUndo}
        <button class="toast-close" type="button" onclick={onUndo}>Undo</button>
    {/if}
    <button class="toast-close" type="button" onclick={dismiss}>X</button>
</div>

<style>
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
                height: 22px;
                width: 22px;
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
                padding: 6px 10px;
                width: auto;
            }
        }
    }
</style>
