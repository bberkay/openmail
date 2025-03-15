<script module lang="ts">
    export type AlertType = "info" | "success" | "error";
</script>

<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Elements/Button";
    import Icon from "$lib/ui/Elements/Icon";

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
    <div class="alert-icon">
        <Icon name={type} />
    </div>
    <div>{@html content}</div>
    {#if closeable}
        <Button.Basic
            type="button"
            class="alert-close"
            onclick={dismiss}
        >
            X
        </Button.Basic>
    {/if}
</div>

<style>
    :global {
        .alert {
            /* TODO: Check this later */
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-sm);
            font-size: var(--font-size-sm);
            opacity: 0;
            transform: translateX(-100%);
            transition: all var(--transition-normal) var(--ease-default);
            box-shadow: var(--shadow-sm);
            display: flex;
            align-items: center;
            gap: var/(--spacing-sm);
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

            &.show {
                opacity: 1;
                transform: translateX(0);
            }

            & .alert-close {
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
        }
    }
</style>
