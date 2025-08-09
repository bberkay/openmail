<script lang="ts">
    import { combine } from "$lib/utils";
    import { onMount, type Snippet } from "svelte";

    interface Props {
        selector: string;
        beforeOpen?: ((target: HTMLElement) => void) | ((target: HTMLElement) => Promise<void>);
        afterClose?: ((target: HTMLElement) => void) | ((target: HTMLElement) => Promise<void>);
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        selector,
        beforeOpen,
        afterClose,
        children,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    let targetElements: NodeListOf<HTMLElement>;
    let currentTarget: HTMLElement;
    let cursor = $state({ x: 0, y: 0 });
    let menu = $state({ w: 0, h: 0 });
    let browser = $state({ w: 0, h: 0 });
    let showMenu = $state(false);

    async function rightClickContextMenu(e: MouseEvent, target: HTMLElement) {
        e.preventDefault();
        currentTarget = target;
        currentTarget.classList.add("context-menu-toggled");
        if (beforeOpen) await beforeOpen(currentTarget);
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

    async function onPageClick(e: MouseEvent) {
        if (!showMenu) return;
        targetElements.forEach((targetElement) =>
            targetElement.classList.remove("context-menu-toggled"),
        );
        showMenu = false;
        if (afterClose) await afterClose(currentTarget);
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
        targetElements = document.querySelectorAll<HTMLElement>(selector)!;
        targetElements.forEach((targetElement) => {
            targetElement.addEventListener("contextmenu", (e) =>
                rightClickContextMenu(e, targetElement)
            )
        });
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
            oncontextmenu={(e) => {
                e.preventDefault();
            }}
            class={combine("context-menu", additionalClass)}
            {...restAttributes}
        >
            {@render children()}
        </div>
    </div>
{/if}

<style>
    :global {
        .context-menu {
            display: inline-flex;
            width: max-content;
            background-color: var(--color-border-subtle);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-md);
            overflow: hidden;
            flex-direction: column;
            justify-content: start;

            & .context-menu-toggled {
                background-color: var(--color-hover);
                outline: 1px solid var(--color-border-subtle);
            }
        }
    }
</style>
