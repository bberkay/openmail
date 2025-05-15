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
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { showThis as showContentOfSettings } from "$lib/ui/Layout/Main/Content/Settings/Content.svelte";
    import Settings from "./Content/Settings.svelte";
    import Accounts from "./Content/Settings/Content/Accounts.svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

    function manageFailedAccounts() {
        showContent(Settings);
        showContentOfSettings(Accounts);
    }

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("check-out-accounts-alert-container", {
                content: local.accounts_failed_to_connect[DEFAULT_LANGUAGE],
                type: "error",
                details: "There are some failed account/mailbox connections you should manage.",
                onManage: manageFailedAccounts,
                onManageText: local.manage_accounts[DEFAULT_LANGUAGE],
                closeable: false
            });
        }
    });
</script>

<div class="content" bind:this={sectionContainer}>
    <div class="alert-container" id="check-out-settings-accounts-alert-container"></div>
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
