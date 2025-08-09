import Tooltip from "./Tooltip.svelte";
import type { Action } from "svelte/action";
import { mount, unmount } from "svelte";

const HOVER_TIME_MS = 500;

let mountedTooltip: Record<string, any> | null = null;
let hoverTimer: ReturnType<typeof setTimeout> | null = null;
let speedUpNextTooltip = false;
let resetSpeedUpInterval: ReturnType<typeof setTimeout> | null = null;

export const show: Action<HTMLElement, string | unknown> = (
    node: HTMLElement,
    content: string | unknown,
) => {
    const contentText = typeof content === "string" ? content : node.innerText;

    function mountTooltip() {
        const mountWrapper = () => {
            mountedTooltip = mount(Tooltip, {
                target: node,
                props: { content: contentText },
                intro: true
            });
            speedUpNextTooltip = true;
        }

        if (speedUpNextTooltip) {
            if (resetSpeedUpInterval)
                clearTimeout(resetSpeedUpInterval);
            mountWrapper();
        } else {
            hoverTimer = setTimeout(mountWrapper, HOVER_TIME_MS);
        }
    }

    function unmountTooltip() {
        if (hoverTimer) {
            clearTimeout(hoverTimer);
            hoverTimer = null;
        }

        if (mountedTooltip) {
            unmount(mountedTooltip, { outro: true });
            mountedTooltip = null;
            resetSpeedUpInterval = setTimeout(() => {
                speedUpNextTooltip = false;
            }, HOVER_TIME_MS)
        }
    }

    node.style.whiteSpace = "nowrap";
    node.style.overflow = "hidden";
    node.style.textOverflow = "ellipsis";

    node.addEventListener("mouseenter", mountTooltip);
    node.addEventListener("mouseleave", unmountTooltip);
    document.addEventListener("scroll", unmountTooltip);

    $effect(() => {
        return () => {
            unmountTooltip();
            node.removeEventListener("mouseenter", mountTooltip);
            node.removeEventListener("mouseleave", unmountTooltip);
            document.addEventListener("scroll", unmountTooltip);
        };
    });
};
