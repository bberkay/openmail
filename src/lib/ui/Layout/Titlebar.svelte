<script>
    import { getCurrentWindow } from '@tauri-apps/api/window';
    import { onMount } from "svelte";
    import Icon from "$lib/ui/Components/Icon";

    const appWindow = getCurrentWindow();

    onMount(() => {
        document
          .getElementById('titlebar-minimize')
          ?.addEventListener('click', () => appWindow.minimize());
        document
          .getElementById('titlebar-maximize')
          ?.addEventListener('click', () => appWindow.toggleMaximize());
        document
          .getElementById('titlebar-close')
          ?.addEventListener('click', () => appWindow.close());
    });
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
            border-top-left-radius: var(--radius-md);
            border-top-right-radius: var(--radius-md);

            & .titlebar-button {
                display: inline-flex;
                justify-content: center;
                align-items: center;
                width: var(--titlebar-height);
                height: var(--titlebar-height);
                user-select: none;
                -webkit-user-select: none;

                &:hover {
                    background: var(--color-hover);
                }
            }
        }
    }
</style>
