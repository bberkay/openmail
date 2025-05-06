<script lang="ts">
    import { onMount } from "svelte";
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        disabled?: boolean;
        inline?: boolean;
        [attribute: string]: unknown;
    }

    let {
        children,
        disabled = false,
        inline = false,
        ...attributes
    }: Props = $props();

    const { class: additionalClass, ...restAttributes } = attributes;

    let container: HTMLElement;
    let toggle: HTMLElement;
    let content: HTMLElement;
    let isOpen: boolean = false;

    const closeSiblingDropdowns = (e: Event) => {
        const parentDropdown = container.parentElement!.closest(".dropdown-container");
        if (parentDropdown) {
            const siblingContent = parentDropdown
                .querySelector<HTMLElement>(".dropdown-container.inline .dropdown-content:not(.hidden)")
            if (siblingContent !== content) {
                siblingContent?.classList.add("hidden");
            }
        }
    }

    const closeWhenClickedOutside = (e: Event) => {
        if (isOpen && !container.contains(e.target as HTMLElement)) {
            content.classList.add("hidden");
        }
    };

    const toggleDropdown = (e: Event) => {
        if (inline) {
            e.stopPropagation();
            closeSiblingDropdowns(e);
        }
        if (!disabled) {
            content.classList.toggle("hidden");
            isOpen = !content.classList.contains("hidden");
        }
    };

    onMount(() => {
        toggle = container.querySelector(".dropdown-toggle")!;
        toggle.addEventListener("click", toggleDropdown);
        toggle.addEventListener("keydown", toggleDropdown);
        content = container.querySelector(".dropdown-content")!;
    });
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={container}
    class={combine(
        `
            dropdown-container
            ${disabled ? "disabled" : ""}
            ${inline ? "inline" : ""}
        `,
        additionalClass,
    )}
    {...restAttributes}
>
    {@render children()}
</div>

<style>
    :global {
        .dropdown-container {
            position: relative;
            width: max-content;

            &:not(:has(> .dropdown-content.hidden)) .dropdown-toggle {
                border-color: var(--color-text-primary);
            }

            .dropdown-item:first-child {
                border-top: none;
            }
        }
    }
</style>
