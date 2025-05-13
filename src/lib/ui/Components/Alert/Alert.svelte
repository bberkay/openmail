<script lang="ts">
    import { onDestroy } from "svelte";
    import { close, type Props } from "./index";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import { combine } from "$lib/utils";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
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

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    let alert: HTMLElement;
    onDestroy(() => {
        dismiss();
    });

    function dismiss() {
        alert.classList.remove("show");
        close(id);
    }

    const onManageWrapper = async (e: Event) => {
        if (onManage) onManage(e);
        dismiss();
    }
</script>

<div
    bind:this={alert}
    class={combine("alert show", type, additionalClass)}
    {...restAttributes}
>
    <div class="alert-body">
        <div class="alert-body-text">
            <div class="alert-icon">
                <Icon name={type} />
            </div>
            <div>
                {@html content}
            </div>
        </div>
        <div class="alert-body-action">
            {#if onManage}
                <Button.Action
                    type="button"
                    class="btn-outline btn-sm alert-manage"
                    onclick={onManageWrapper}
                >
                    {onManageText || local.manage[DEFAULT_LANGUAGE]}
                </Button.Action>
            {/if}
            {#if closeable}
                <Button.Basic
                    type="button"
                    class="btn-outline btn-sm alert-close"
                    onclick={dismiss}
                >
                    <Icon name="close" />
                </Button.Basic>
            {/if}
        </div>
    </div>
    {#if details}
        <div class="alert-details">
            <Collapse title="Details" openAtStart={false}>
                <div class="separator"></div>
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
            padding-bottom: 0;
            border-radius: var(--radius-md);
            font-size: var(--font-size-sm);
            opacity: 0;
            box-shadow: var(--shadow-sm);
            gap: var(--spacing-sm);
            width: 100%;

            &.error {
                background-color: var(--color-error-bg);
                border: 1px solid var(--color-error-border);
                border-left: 2px solid var(--color-error-text);
                color: var(--color-error-text);

                & .alert-manage {
                    border-color: var(--color-error-border);
                    color: var(--color-error-text);
                    background-color: var(--color-error-bg);
                }

                & .separator {
                    background-color: var(--color-error-border);
                }

                & svg {
                    fill: var(--color-error-text);
                }
            }

            &.warning {
                background-color: var(--color-warning-bg);
                border: 1px solid var(--color-warning-border);
                border-left: 2px solid var(--color-warning-text);
                color: var(--color-warning-text);

                & .alert-manage {
                    border-color: var(--color-warning-border);
                    color: var(--color-warning-text);
                    background-color: var(--color-warning-bg);
                }

                & .separator {
                    background-color: var(--color-warning-border);
                }

                & svg {
                    fill: var(--color-warning-text);
                }
            }

            &.info {
                background-color: var(--color-info-bg);
                border: 1px solid var(--color-info-border);
                border-left: 2px solid var(--color-info-text);
                color: var(--color-info-text);

                & .alert-manage {
                    border-color: var(--color-info-border);
                    color: var(--color-info-text);
                    background-color: var(--color-info-bg);
                }

                & .separator {
                    background-color: var(--color-info-border);
                }

                & svg {
                    fill: var(--color-info-text);
                }
            }

            &.success {
                background-color: var(--color-success-bg);
                border: 1px solid var(--color-success-border);
                border-left: 2px solid var(--color-success-text);
                color: var(--color-success-text);

                & .alert-manage {
                    border-color: var(--color-success-border);
                    color: var(--color-success-text);
                    background-color: var(--color-success-bg);
                }

                & .separator {
                    background-color: var(--color-success-border);
                }

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

                & .alert-body-text {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-sm);
                }

                & .alert-icon {
                    margin-bottom: -4px;

                    & svg {
                        width: var(--font-size-xl)!important;
                        height: var(--font-size-xl)!important;
                    }
                }

                & .alert-manage {
                    &:hover {
                        filter: brightness(1.2);
                    }

                    &:active {
                        filter: brightness(0.9);
                    }
                }

                & .alert-close {
                    background: transparent;
                    border: transparent;

                    &:hover {
                        background: rgba(255, 255, 255, 0.2);
                    }

                    &:active {
                        background: rgba(255, 255, 255, 0.1);
                    }
                }

                & .alert-body-action {
                    display: flex;
                    gap: var(--spacing-sm);
                }
            }

            & .alert-details {
                font-size: var(--font-size-xs);

                & svg {
                    width: var(--font-size-md);
                    height: var(--font-size-md);
                }

                & .collapse-header {
                    padding: var(--spacing-sm) var(--spacing-2xs);
                    padding-bottom: 0;
                    margin-right: var(--spacing-2xs);
                }

                & .collapse-content {
                    padding: var(--spacing-sm) var(--spacing-2xs);
                }

                & .separator {
                    margin-bottom: var(--spacing-sm);
                }
            }
        }
    }
</style>
