<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import General from "./Content/General.svelte";
    import Appearance from "./Content/Appearance.svelte";
    import Mailbox from "./Content/Mailbox.svelte";
    import Accounts from "./Content/Accounts.svelte";
    import Notifications from "./Content/Notifications.svelte";
    import About from "./Content/About.svelte";
    import { showThis as showContent } from "./Content.svelte";

    const makeMenuShown = (e: Event) => {
        document.querySelector(".settings-title-btn.shown")?.classList.remove("shown");
        const newTarget = e.target as HTMLElement;
        newTarget.classList.add("shown");
    }

    const showClickedSettings = (e: Event, component: any) => {
        makeMenuShown(e);
        showContent(component);
    }
</script>

<div class="settings-menu">
    <div class="settings-menu-left">
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn shown"
            onclick={(e: Event) => showClickedSettings(e, General)}
        >
            General
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => showClickedSettings(e, Appearance)}
        >
            Appearance
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => showClickedSettings(e, Mailbox)}
        >
            Mailbox
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => showClickedSettings(e, Accounts)}
        >
            Accounts
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => showClickedSettings(e, Notifications)}
        >
            Notifications
        </Button.Basic>
        <Button.Basic
            type="button"
            class="btn-inline settings-title-btn"
            onclick={(e: Event) => showClickedSettings(e, About)}
        >
            About
        </Button.Basic>
    </div>
    <div class="settings-menu-right">
        <Button.Action
            type="button"
            class="btn-inline settings-operation-btn"
            onclick={() => {}}
        >
            Reset to default
        </Button.Action>
        <Button.Action
            type="submit"
            class="btn-outline settings-operation-btn"
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

                    & .settings-operation-btn {
                        font-size: var(--font-size-xs);
                    }
                }
            }
        }
    }
</style>
