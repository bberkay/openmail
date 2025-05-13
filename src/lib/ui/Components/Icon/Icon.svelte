<script lang="ts">
    import { onMount } from "svelte";
    import { createDomElement } from "$lib/utils";

    interface Props {
        name: string;
        [attribute: string]: string;
    }

    let {
        name,
        ...attributes
    }: Props = $props();

    let placeholder: HTMLElement;
    onMount(async () => {
        const svgContent = (await import(`$lib/assets/icons/${name}.svg?raw`)).default;
        const svgElement = createDomElement(svgContent);
        svgElement.setAttribute("name", name);
        if (svgElement) {
            Object.entries(attributes).forEach(([key, value]) => {
                svgElement.setAttribute(key, value);
            });
        }
        placeholder.replaceWith(svgElement);
    });
</script>

<div bind:this={placeholder}></div>

<style>
    :global {
        svg {
            width: var(--font-size-lg);
            height: var(--font-size-lg);
            stroke: currentColor;
            stroke-width: 2;
            transition: all var(--transition-fast) var(--ease-default);
            fill: var(--color-text-secondary);

            &[name="ellipsis"] {
                stroke-width: 1;
                fill: var(--color-text-secondary)!important;
            }

            &[name="error"] {
                stroke-width: 1;
                fill: var(--color-error-text)!important;
            }
        }
    }
</style>
