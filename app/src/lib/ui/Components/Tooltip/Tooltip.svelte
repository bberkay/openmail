<script lang="ts">
    import { onMount } from "svelte";
    import { fade } from 'svelte/transition';

    const FADE_DURATION_MS = 200;

    interface Props {
        content: string;
    }

    let { content }: Props = $props();

    let container: HTMLElement;
    onMount(() => {
        if (typeof content !== "string") {
            content = container.innerText;
        }
        container.innerText = content;
        positionTooltip();
    });

    function positionTooltip() {
        const tooltipRect = container.getBoundingClientRect();

        const horizontanlPosition = "0px";
        if (tooltipRect.right > window.innerWidth) {
            container.style.right = horizontanlPosition;
        } else {
            container.style.left = horizontanlPosition;
        }

        const verticalPosition = `${container.offsetTop}px`;
        if (tooltipRect.bottom > window.innerHeight) {
            container.style.bottom = verticalPosition;
        } else {
            container.style.top = verticalPosition;
        }
    }
</script>

<div transition:fade={{ duration: FADE_DURATION_MS }} bind:this={container} class="tooltip" tabindex="-1"></div>

<style>
    :global {
        .fit {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .tooltip {
            position: absolute;
            border: 1px solid var(--color-gray);
            width: max-content;
            background-color: var(--color-border);
            color: var(--color-text-primary);
            padding: var(--spacing-2xs) var(--spacing-xs);
            border-radius: var(--radius-sm);
            z-index: var(--z-index-tooltip);
            cursor: auto;
        }
    }
</style>
