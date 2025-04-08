<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { close, type AlertType } from "./index";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";

    interface Props {
        id: string;
        content: string;
        type: AlertType;
        closeable?: boolean;
        details?: string;
        onManage?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        onManageText?: string;
    }

    let {
        id,
        content,
        type,
        closeable,
        details,
        onManage,
        onManageText
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

    const onManageWrapper = async (e: Event) => {
        if (onManage) onManage(e);
        dismiss();
    }
</script>

<div class="alert {type}" bind:this={alert}>
    <div class="alert-content">
        <div class="alert-icon">
            <Icon name={type} />
        </div>
        <div class="alert-body">
            <div class="alert-type">
                <span>{type}</span>
            </div>
            <div class="alert-content">
                {@html content}
            </div>
        </div>
        <div>
            {#if onManage}
                <Button.Action
                    type="button"
                    class="alert-manage"
                    onclick={onManageWrapper}
                >
                    {onManageText || "Manage"}
                </Button.Action>
            {/if}
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
    </div>
    {#if details}
        <div class="alert-details">
            <Collapse title="Details" openAtStart={false}>
                {@html details}
            </Collapse>
        </div>
    {/if}
</div>

<style>
    :global {
        .alert {
            background-color: var(--color-bg-primary);
            color: var(--color-text-primary);
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-sm);
            font-size: var(--font-size-sm);
            opacity: 0;
            transform: translateX(-100%);
            transition: all var(--transition-normal) var(--ease-default);
            box-shadow: var(--shadow-sm);
            gap: var(--spacing-sm);
            width: max-content;

            &.error {
                border: 1px solid var(--color-error);
                color: var(--color-error);
            }

            &.warning {
                border: 1px solid var(--color-warning);
                color: var(--color-warning);
            }

            &.info {
                border: 1px solid var(--color-info);
                color: var(--color-info);
            }

            &.success {
                border: 1px solid var(--color-success);
                color: var(--color-success);
            }

            &.show {
                opacity: 1;
                transform: translateX(0);
            }

            & .alert-content {
                display: flex;
                align-items: center;
                justify-content:space-between;

                & .alert-icon svg {
                    width: var(--font-size-lg)!important;
                    height: var(--font-size-lg)!important;
                }

                & .alert-body{
                    flex-grow:1;
                    margin-left: var(--spacing-2xs);
                    margin-right: var(--spacing-md);

                    & .alert-type {
                        text-transform: capitalize;
                        font-weight: bold;
                    }
                }

                & .alert-close {
                    background: none;
                    border: none;
                    font-size: var(--font-size-md);
                    cursor: pointer;
                    padding: 0;
                }
            }
        }
    }
</style>
