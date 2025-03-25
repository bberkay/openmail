<script lang="ts">
    import { onMount, type Snippet } from "svelte";

    interface Props {
        target: string;
        children: Snippet;
    }

    let { target, children } = $props();
    let cursor = $state({ x: 0, y: 0 });
    let menu = $state({ w: 0, h: 0 });
    let browser = $state({ w: 0, h: 0 });
    let showMenu = $state(false);

    function rightClickContextMenu(e: MouseEvent) {
        e.preventDefault();
        showMenu = true;
        browser = {
            w: window.innerWidth,
            h: window.innerHeight,
        };
        cursor = {
            x: e.clientX,
            y: e.clientY,
        };
        if (browser.h - cursor.y < menu.h) cursor.y = cursor.y - menu.h;
        if (browser.w - cursor.x < menu.w) cursor.x = cursor.x - menu.w;
    }

    function onPageClick(e: MouseEvent) {
        showMenu = false;
    }

    function getContextMenuDimension(node: HTMLElement) {
        let height = node.offsetHeight;
        let width = node.offsetWidth;
        menu = {
            h: height,
            w: width,
        };
    }

    onMount(() => {
        document
            .getElementById(target)!
            .addEventListener("contextmenu", rightClickContextMenu);
    });
</script>

<svelte:window onclick={onPageClick} />

{#if showMenu}
    <div
        use:getContextMenuDimension
        style="position: absolute; top:{cursor.y}px; left:{cursor.x}px"
    >
        <div
            role="menu"
            tabindex="0"
            class="context-menu"
            oncontextmenu={(e) => {
                e.preventDefault();
            }}
        >
            {@render children()}
        </div>
    </div>
{/if}

<style>
    * {
        padding: 0;
        margin: 0;
    }
    .context-menu {
        display: inline-flex;
        width: max-content;
        background-color: var(--color-border-subtle);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        overflow: hidden;
        flex-direction: column;
    }
</style>
