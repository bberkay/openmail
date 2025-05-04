<script lang="ts">
    import { combine } from "$lib/utils";
    import { onMount } from "svelte";
    import { type Snippet } from "svelte";

    interface Props {
        children: Snippet;
        disabled?: boolean;
        [attribute: string]: unknown;
    }

    let {
        children,
        disabled = false,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let container: HTMLElement;
    let toggle: HTMLElement;
    let content: HTMLElement;
    let isOpen: boolean = false;

    const closeWhenClickedOutside = (e: Event) => {
        if (isOpen && !container.contains(e.target as HTMLElement)) {
            content.classList.add("hidden");
        }
    };

    const togglePopover = (e: Event) => {
        if (!disabled) {
            content.classList.toggle("hidden");
            isOpen = !content.classList.contains("hidden");
        }
    };

    onMount(() => {
        toggle = container.querySelector(
            ".popover-toggle",
        )!;
        toggle.addEventListener("click", togglePopover);
        toggle.addEventListener("keydown", togglePopover);
        content = container.querySelector(".popover-content")!;
    });
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={container}
    class={combine(`popover-container ${disabled ? "disabled" : ""}`, additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .popover-container {
            position: relative;
            z-index: var(--z-index-popover);
            width: max-content;
        }

        .popover-container.disabled {
            pointer-events: none!important;
            cursor: auto;
            filter: brightness(0.7)!important;
        }
    }
</style>
