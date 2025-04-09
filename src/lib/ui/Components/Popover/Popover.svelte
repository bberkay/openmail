<script lang="ts">
    import { combine } from "$lib/utils";
    import { onMount } from "svelte";
    import { type Snippet } from "svelte";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let popoverContainer: HTMLElement;
    let toggleContainer: HTMLElement;
    let contentContainer: HTMLElement;

    const closeWhenClickedOutside = (e: Event) => {
        if (!popoverContainer.contains(e.target as HTMLElement)) {
            contentContainer.classList.add("hidden");
        }
    };

    const toggleDropdown = (e: Event) => {
        e.stopPropagation();
        contentContainer.classList.toggle("hidden");
    };

    onMount(() => {
        toggleContainer = popoverContainer.querySelector(
            ".dropdown-toggle-container",
        )!;
        toggleContainer.addEventListener("click", toggleDropdown);
        toggleContainer.addEventListener("keydown", toggleDropdown);
        contentContainer =
            popoverContainer.querySelector(".popover-content")!;
    });
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={popoverContainer}
    class={combine("popover-container", additionalClass)}
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
    }
</style>
