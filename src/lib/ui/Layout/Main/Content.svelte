<script module lang="ts">
    import { display, destroy } from "../Section.svelte";
    import { type Snippet } from "svelte";

    let sectionContainer: HTMLElement;
    let isMounted = $state(false);
    export function showThis(section: any, props?: any) {
        isMounted = true;
        display(section, sectionContainer, props);
    }

    export function backToDefault() {
        destroy();
        isMounted = false;
    }
</script>

<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { getFailedMailboxOrFoldersTemplate } from "$lib/templates";
    import { createSenderAddress } from "$lib/utils";
    import { MailboxController } from "$lib/controllers/MailboxController";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

    $effect(() => {
        if (
            SharedStore.failedMailboxes.length > 0 ||
            SharedStore.failedFolders.length > 0
        ) {
            showAlert("mailboxes-alert-container", {
                content: `There were some mailboxes and/or folders that failed to retrive.`,
                type: "error",
                details: getFailedMailboxOrFoldersTemplate(
                    SharedStore.failedMailboxes
                        .map((account) => {
                            return `<li>${createSenderAddress(account.email_address, account.fullname)}</li>`;
                        })
                        .join(""),
                    SharedStore.failedFolders
                        .map((account) => {
                            return `<li>${createSenderAddress(account.email_address, account.fullname)}</li>`;
                        })
                        .join(""),
                ),
                onManage: async () => {
                    await MailboxController.init(true);
                },
                onManageText: "Retry",
            });
        }
    });
</script>

<div class="content" bind:this={sectionContainer}>
    <div class="alert-container" id="mailboxes-alert-container"></div>
    <div class="alert-container" id="folders-alert-container"></div>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>

<style>
    :global {
        .content {
            width: 80%;
            margin-top: var(--spacing-xl);

            &:has(.compose) {
                width: 50%;
            }

            &:has(.email) {
                width: 70%;
            }

            & .toolbox {
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                width: 100%;
                padding: var(--spacing-sm) var(--spacing-lg);

                & .toolbox-left {
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    gap: var(--spacing-xl);
                }

                & .toolbox-right {
                    & .pagination {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        font-size: var(--font-size-sm);
                        gap: var(--spacing-md);
                        color: var(--color-text-secondary);

                        & svg {
                            margin-top: var(--spacing-2xs);
                        }
                    }
                }
            }
        }
    }
</style>
