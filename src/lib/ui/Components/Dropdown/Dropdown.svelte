<script lang="ts">
    import { onMount, onDestroy, setContext } from "svelte";
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

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    let container: HTMLElement;
    let toggle: HTMLElement;
    let content: HTMLElement;
    let isOpen: boolean = false;

    function closeSiblingDropdowns(e: Event) {
        const parentDropdown = container.parentElement!.closest(
            ".dropdown-container",
        );
        if (parentDropdown) {
            const siblingContent = parentDropdown.querySelector<HTMLElement>(
                ".dropdown-container.inline .dropdown-content:not(.hidden)",
            );
            if (siblingContent !== content) {
                siblingContent?.classList.add("hidden");
            }
        }
    }

    function restructureInlineDropdown() {
        if (!inline) return;

        if (isOpen) {
            document.body.append(content);
        } else {
            container.append(content);
        }

        repositionInlineDropdown();

        const parentDropdownContent = container.parentElement?.
            closest(".dropdown-container")?.
            querySelector(".dropdown-content");
        if (parentDropdownContent) {
            if (isOpen) {
                parentDropdownContent.addEventListener("scroll", repositionInlineDropdown);
            } else {
                parentDropdownContent.removeEventListener("scroll", repositionInlineDropdown);
            }
        }
    }

    function repositionInlineDropdown() {
        if (!inline) return;

        if (isOpen) {
            const toggleRect = toggle.getBoundingClientRect();
            const scrollX = window.scrollX || document.documentElement.scrollLeft;
            const scrollY = window.scrollY || document.documentElement.scrollTop;

            const dropdownWidth = content.offsetWidth;
            const dropdownHeight = content.offsetHeight;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            let top = toggleRect.bottom + scrollY;
            let left = toggleRect.left + scrollX;

            // Prevent right overflow
            if (left + dropdownWidth > scrollX + viewportWidth) {
                // 10px padding
                left = scrollX + viewportWidth - dropdownWidth - 10;
            }

            // Prevent bottom overflow
            if (top + dropdownHeight > scrollY + viewportHeight) {
                const aboveTop = toggleRect.top + scrollY - dropdownHeight;
                if (aboveTop >= scrollY) {
                    // show at the top of the toggle
                    top = aboveTop;
                } else {
                    // show at the bottom of the toggle
                    top = scrollY + viewportHeight - dropdownHeight - 10;
                }
            }

            content.style.top = `${top}px`;
            content.style.left = `${left}px`;
        } else {
            content.style.top = "";
            content.style.left = "";
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
            restructureInlineDropdown();
        }
    };

    setContext('close-dropdown', toggleDropdown);

    onMount(() => {
        toggle = container.querySelector(".dropdown-toggle")!;
        toggle.addEventListener("click", toggleDropdown);
        toggle.addEventListener("keydown", toggleDropdown);
        content = container.querySelector(".dropdown-content")!;
        container.addEventListener("closeDropdown", toggleDropdown);
    });

    onDestroy(() => {
        container.removeEventListener("closeDropdown", toggleDropdown);
    })
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

            &.dropdown-sm {
                width: 140px;

                & .dropdown-toggle {
                    padding: var(--spacing-2xs) var(--spacing-2xs);
                    font-size: var(--font-size-xs);
                }

                & .dropdown-content .dropdown-item {
                    font-size: var(--font-size-xs);
                }
            }

            &:not(:has(> .dropdown-content.hidden)) .dropdown-toggle {
                border-color: var(--color-text-primary);
            }

            & .dropdown-item:first-child {
                border-top: none;
            }
        }
    }
</style>
