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
                background-color: var(--color-bg-error);
                border: 1px solid var(--color-border-error);
                border-left: 2px solid var(--color-text-error);
                color: var(--color-text-error);

                & .alert-manage {
                    border-color: var(--color-border-error);
                    color: var(--color-text-error);
                    background-color: var(--color-bg-error);
                }

                & .separator {
                    background-color: var(--color-border-error);
                }

                & svg {
                    fill: var(--color-text-error);
                }
            }

            &.warning {
                background-color: var(--color-bg-warning);
                border: 1px solid var(--color-border-warning);
                border-left: 2px solid var(--color-text-warning);
                color: var(--color-text-warning);

                & .alert-manage {
                    border-color: var(--color-border-warning);
                    color: var(--color-text-warning);
                    background-color: var(--color-bg-warning);
                }

                & .separator {
                    background-color: var(--color-border-warning);
                }

                & svg {
                    fill: var(--color-text-warning);
                }
            }

            &.info {
                background-color: var(--color-bg-info);
                border: 1px solid var(--color-border-info);
                border-left: 2px solid var(--color-text-info);
                color: var(--color-text-info);

                & .alert-manage {
                    border-color: var(--color-border-info);
                    color: var(--color-text-info);
                    background-color: var(--color-bg-info);
                }

                & .separator {
                    background-color: var(--color-border-info);
                }

                & svg {
                    fill: var(--color-text-info);
                }
            }

            &.success {
                background-color: var(--color-bg-success);
                border: 1px solid var(--color-border-success);
                border-left: 2px solid var(--color-text-success);
                color: var(--color-text-success);

                & .alert-manage {
                    border-color: var(--color-border-success);
                    color: var(--color-text-success);
                    background-color: var(--color-bg-success);
                }

                & .separator {
                    background-color: var(--color-border-success);
                }

                & svg {
                    fill: var(--color-text-success);
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
