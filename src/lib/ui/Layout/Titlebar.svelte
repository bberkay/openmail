<script lang="ts">
    import { getCurrentWindow } from '@tauri-apps/api/window';
    import { onMount } from "svelte";
    import Icon from "$lib/ui/Components/Icon";

    const TITLEBAR_RADIUS_VAR_NAME = "--titlebar-radius";

    const appWindow = getCurrentWindow();
    let originalTitlebarRadius: string | null = null;

    onMount(() => {
        originalTitlebarRadius = getTitlebarRadius();

        document
          .getElementById('titlebar-minimize')!
          .addEventListener('click', () => appWindow.minimize());
        document
          .getElementById('titlebar-maximize')!
          .addEventListener('click', () => appWindow.toggleMaximize());
        document
          .getElementById('titlebar-close')!
          .addEventListener('click', () => appWindow.close());

        appWindow.onResized(handleAppRadiusOnResize);
    });

    function resetTitlebarRadius() {
        document.documentElement.style.setProperty(
            TITLEBAR_RADIUS_VAR_NAME,
            originalTitlebarRadius
        );
    }

    function removeTitlebarRadius() {
        document.documentElement.style.setProperty(
            TITLEBAR_RADIUS_VAR_NAME,
            "0px"
        );
    }

    function getTitlebarRadius() {
        return getComputedStyle(document.documentElement)
            .getPropertyValue(TITLEBAR_RADIUS_VAR_NAME)
    }

    async function handleAppRadiusOnResize() {
        const isFullscreen = await appWindow.isMaximized();
        if (isFullscreen) {
            removeTitlebarRadius();
        } else {
            resetTitlebarRadius();
        }
    }
</script>

<div data-tauri-drag-region class="titlebar">
    <div class="titlebar-button" id="titlebar-minimize">
        <Icon name="minimize" />
    </div>
    <div class="titlebar-button" id="titlebar-maximize">
        <Icon name="maximize" />
    </div>
    <div class="titlebar-button" id="titlebar-close">
        <Icon name="close" />
    </div>
</div>

<style>
    :global {
        .titlebar {
            height: var(--titlebar-height);
            background: transparent;
            user-select: none;
            display: flex;
            justify-content: flex-end;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            border: none;
            border-top-left-radius: var(--titlebar-radius);
            border-top-right-radius: var(--titlebar-radius);
            z-index: var(--z-index-titlebar);

            & .titlebar-button {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                width: var(--titlebar-height);
                height: var(--titlebar-height);
                user-select: none;
                -webkit-user-select: none;

                & svg {
                    width: var(--font-size-md);
                    height: var(--font-size-md);
                }

                &:hover {
                    background: var(--color-hover);
                }
            }
        }
    }
</style>
