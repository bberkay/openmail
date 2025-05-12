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
    import { getFailedAccountsTemplate, getFailedItemTemplate, getFailedMailboxOrFoldersTemplate } from "$lib/templates";
    import { createSenderAddress } from "$lib/utils";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("accounts-alert-container", {
                content: local.accounts_failed_to_connect[DEFAULT_LANGUAGE],
                type: "error",
                details: getFailedAccountsTemplate(
                    SharedStore.failedAccounts
                        .map((account) => {
                            return getFailedItemTemplate(
                                createSenderAddress(account.email_address, account.fullname)
                            )
                        })
                        .join(""),
                ),
                onManage: () => {
                    // TODO: showContent account list on settings.
                },
                onManageText: local.manage_accounts[DEFAULT_LANGUAGE],
                closeable: true
            });
        }

        if (
            SharedStore.accountsWithFailedMailboxes.length > 0 ||
            SharedStore.accountsWithFailedFolders.length > 0
        ) {
            showAlert("mailboxes-or-folders-alert-container", {
                content: local.error_failed_mailboxes_or_folders[DEFAULT_LANGUAGE],
                type: "error",
                details: getFailedMailboxOrFoldersTemplate(
                    SharedStore.accountsWithFailedMailboxes
                        .map((account) => {
                            return getFailedItemTemplate(
                                createSenderAddress(account.email_address, account.fullname)
                            )
                        })
                        .join(""),
                    SharedStore.accountsWithFailedFolders
                        .map((account) => {
                            return getFailedItemTemplate(
                                createSenderAddress(account.email_address, account.fullname)
                            )
                        })
                        .join(""),
                ),
                onManage: async () => {
                    await MailboxController.init(true);
                },
                onManageText: local.retry[DEFAULT_LANGUAGE],
                closeable: true
            });
        }
    });
</script>

<div class="content" bind:this={sectionContainer}>
    <div class="alert-container" id="accounts-alert-container"></div>
    <div class="alert-container" id="mailboxes-or-folders-alert-container"></div>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>

<style>
    :global {
        .content {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: var(--spacing-2xl);
            height: 100%;

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
