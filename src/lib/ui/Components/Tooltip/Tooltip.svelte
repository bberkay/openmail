<script lang="ts">
    import { onMount } from "svelte";
    import { fade } from 'svelte/transition';

    interface Props {
        content: string;
    }

    let { content }: Props = $props();

    let parent: HTMLElement;
    let container: HTMLElement;
    onMount(() => {
        parent = container.parentElement as HTMLElement;
        if (typeof content !== "string") {
            content = parent.innerText;
        }
        container.innerText = content;
        positionTooltip();
    });

    function positionTooltip() {
        const GAP = 4;
        const tooltipRect = container.getBoundingClientRect();

        const horizontanlPosition = "0px";
        if (tooltipRect.right > window.innerWidth) {
            container.style.right = horizontanlPosition;
        } else {
            container.style.left = horizontanlPosition;
        }

        const verticalPosition = `${tooltipRect.height + GAP}px`;
        if (tooltipRect.bottom > window.innerHeight) {
            container.style.bottom = verticalPosition;
        } else {
            container.style.top = verticalPosition;
        }
    }
</script>

<div transition:fade={{ duration: 200 }} bind:this={container} class="tooltip" tabindex="-1"></div>

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
