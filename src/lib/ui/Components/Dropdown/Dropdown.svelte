<script lang="ts">
    import { onMount } from "svelte";
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let dropdownContainer: HTMLElement;
    let toggleContainer: HTMLElement;
    let contentContainer: HTMLElement;

    const closeWhenClickedOutside = (e: Event) => {
        if (!dropdownContainer.contains(e.target as HTMLElement)) {
            contentContainer.classList.add("hidden");
        }
    };

    const toggleDropdown = (e: Event) => {
        e.stopPropagation();
        contentContainer.classList.toggle("hidden");
    };

    onMount(() => {
        toggleContainer = dropdownContainer.querySelector(
            ".dropdown-toggle-container",
        )!;
        toggleContainer.addEventListener("click", toggleDropdown);
        toggleContainer.addEventListener("keydown", toggleDropdown);
        contentContainer =
            dropdownContainer.querySelector(".dropdown-content")!;
    });
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={dropdownContainer}
    class={combine("dropdown-container", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .dropdown-container {
            position: relative;
            z-index: var(--z-index-dropdown);
            width: max-content;
        }
    }
</style>
