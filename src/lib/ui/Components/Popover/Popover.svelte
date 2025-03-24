<script lang="ts">
    import { onMount } from "svelte";
    import { type Snippet } from "svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

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

<div class="popover-container" bind:this={popoverContainer}>
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
