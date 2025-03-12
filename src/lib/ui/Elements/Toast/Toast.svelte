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
    .toast {
        background-color: #333;
        color: white;
        padding: 16px 24px;
        border-radius: 4px;
        font-family: Arial, sans-serif;
        font-size: 14px;
        opacity: 0;
        transform: translateX(-100%);
        transition: all 0.3s ease-in;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 200px;
        max-width: 300px;
    }

    :global(.toast.show) {
        opacity: 1;
        transform: translateX(0);
    }

    .toast-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        margin-left: 8px;
        opacity: 0.7;
        transition: opacity 0.2s;

        &:hover {
            opacity: 1;
        }
    }
</style>
