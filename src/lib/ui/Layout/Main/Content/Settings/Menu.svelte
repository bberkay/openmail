<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import General from "./Content/General.svelte";
    import Appearance from "./Content/Appearance.svelte";
    import Mailbox from "./Content/Mailbox.svelte";
    import Accounts from "./Content/Accounts.svelte";
    import Notifications from "./Content/Notifications.svelte";
    import About from "./Content/About.svelte";
    import { showThis as showContent } from "./Content.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { FileSystem } from "$lib/services/FileSystem";
    import Icon from "$lib/ui/Components/Icon";
    import { backToDefault } from "$lib/ui/Layout/Main/Content.svelte";

    const highlightSelectedMenu = (e: Event) => {
        document.querySelector(".settings-title-btn.shown")?.classList.remove("shown");
        const newTarget = (e.target as HTMLElement).closest(".settings-title-btn")!;
        newTarget.classList.add("shown");
    }

    const displaySelectedSettings = (e: Event, component: any) => {
        highlightSelectedMenu(e);
        showContent(component);
    }

    const resetToDefault = async () => {
        SharedStore.preferences = DEFAULT_PREFERENCES;
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences(SharedStore.preferences);
        document.dispatchEvent(new CustomEvent("preferences-reset-to-default"));
    }
</script>

<div class="settings-menu">
    <div class="settings-menu-left">
        <Button.Basic
            type="button"
            class="btn-inline"
            onclick={backToDefault}
        >
            <Icon name="back" />
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn shown"
            onclick={(e: Event) => displaySelectedSettings(e, General)}
        >
            General
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => displaySelectedSettings(e, Appearance)}
        >
            Appearance
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => displaySelectedSettings(e, Mailbox)}
        >
            Mailbox
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => displaySelectedSettings(e, Accounts)}
        >
            {#if
                SharedStore.failedAccounts.length > 0 ||
                SharedStore.accountsWithFailedMailboxes.length > 0 ||
                SharedStore.accountsWithFailedFolders.length > 0
            }
                <Icon name="error" />
            {/if}
            <span>Accounts</span>
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => displaySelectedSettings(e, Notifications)}
        >
            Notifications
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => displaySelectedSettings(e, About)}
        >
            About
        </Button.Basic>
    </div>
    <div class="settings-menu-right">
        <Button.Action
            type="button"
            class="btn-inline btn-md"
            onclick={resetToDefault}
        >
            Reset to default
        </Button.Action>
        <Button.Action
            type="submit"
            class="btn-outline btn-md"
            onclick={() => {}}
        >
            Save changes
        </Button.Action>
    </div>
</div>

<style>
    :global {
        .settings {
            .settings-menu {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                width: 100%;
                padding: var(--spacing-sm) 0;

                & .settings-menu-left {
                    display: flex;
                    flex-direction: row;
                    gap: var(--spacing-xs);

                    & .settings-title-btn {
                        color: var(--color-text-secondary);
                        filter: brightness(0.7);

                        & svg {
                            width: var(--font-size-xl);
                            height: var(--font-size-xl);
                        }

                        &.shown {
                            color: var(--color-text-primary);
                            filter: brightness(1);
                        }
                    }
                }

                & .settings-menu-right {
                    display: flex;
                    flex-direction: row;
                    gap: var(--spacing-sm);
                }
            }
        }
    }
</style>
