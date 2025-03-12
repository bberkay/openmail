<script module lang="ts">
    export type AlertType = "info" | "success" | "error";
</script>

<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import type { Snippet } from "svelte";
    import { close } from "./index";

    interface Props {
        id: string;
        content: string;
        type: AlertType;
        closeable?: boolean;
    }

    let {
        id,
        content,
        type,
        closeable
    }: Props = $props();
    let alert: HTMLElement;

    onMount(() => {
        setTimeout(() => alert.classList.add("show"), 10);
    });

    onDestroy(() => {
        dismiss();
    });

    function dismiss() {
        alert.classList.remove("show");
        alert.addEventListener("transitionend", () => {
            close(id);
        });
    }
</script>

<div class="alert {type}" bind:this={alert}>
    <div>{@html content}</div>
    {#if closeable}
        <button class="alert-close" type="button" onclick={dismiss}>X</button>
    {/if}
</div>

<style>
    .alert {
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

        &.error {
            background-color: red;
        }

        &.success {
            background-color: green;
        }

        &.info {
            background-color: blue;
        }
    }

    :global(.alert.show) {
        opacity: 1;
        transform: translateX(0);
    }

    .alert-close {
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
