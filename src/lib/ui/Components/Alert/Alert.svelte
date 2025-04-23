<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { close, type Props } from "./index";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import { combine } from "$lib/utils";
    import { ANIMATION_INIT_DELAY_MS, DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface PropsWithMountId extends Props {
        id: string;
    }

    let {
        id,
        content,
        type,
        closeable,
        details,
        onManage,
        onManageText,
        ...attributes
    }: PropsWithMountId = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let alert: HTMLElement;
    onMount(() => {
        setTimeout(() => alert.classList.add("show"), ANIMATION_INIT_DELAY_MS);
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

<div
    bind:this={alert}
    class={combine("alert", type, additionalClass)}
    {...restAttributes}
>
    <div class="alert-body">
        <div class="alert-icon">
            <Icon name={type} />
        </div>
        <div>
            {@html content}
        </div>
        <div>
            {#if onManage}
                <Button.Action
                    type="button"
                    class="alert-manage"
                    onclick={onManageWrapper}
                >
                    {onManageText || local.manage[DEFAULT_LANGUAGE]}
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
            color: var(--color-text-primary);
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            font-size: var(--font-size-sm);
            opacity: 0;
            transform: translateX(-100%);
            transition: transform var(--transition-normal) var(--ease-default);
            box-shadow: var(--shadow-sm);
            gap: var(--spacing-sm);
            width: max-content;

            &.error {
                background-color: var(--color-error-bg);
                border: 1px solid var(--color-error-border);
                border-left: 2px solid var(--color-error-text);
                color: var(--color-error-text);

                & svg {
                    fill: var(--color-error-text);
                }
            }

            &.warning {
                background-color: var(--color-warning-bg);
                border: 1px solid var(--color-warning-border);
                border-left: 2px solid var(--color-warning-text);
                color: var(--color-warning-text);

                & svg {
                    fill: var(--color-warning-text);
                }
            }

            &.info {
                background-color: var(--color-info-bg);
                border: 1px solid var(--color-info-border);
                border-left: 2px solid var(--color-info-text);
                color: var(--color-info-text);

                & svg {
                    fill: var(--color-info-text);
                }
            }

            &.success {
                background-color: var(--color-success-bg);
                border: 1px solid var(--color-success-border);
                border-left: 2px solid var(--color-success-text);
                color: var(--color-success-text);

                & svg {
                    fill: var(--color-success-text);
                }
            }

            &.show {
                opacity: 1;
                transform: translateX(0);
            }

            & .alert-body {
                display: flex;
                align-items: center;
                justify-content:space-between;
                gap: var(--spacing-sm);

                & svg {
                    width: var(--font-size-xl)!important;
                    height: var(--font-size-xl)!important;
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
