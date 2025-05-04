<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { combine } from "$lib/utils";
    import { Spinner } from "$lib/ui/Components/Loader";

    interface Props {
        children: Snippet;
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        [attribute: string]: unknown;
    }

    let {
        children,
        onclick,
        ...attributes
    }: Props = $props();

    let dropdownItem: HTMLElement;

    const makeAnAction = async (e: Event) => {
        e.preventDefault();

        dropdownItem.classList.add("disabled");
        const loader = mount(Spinner, {
            target: dropdownItem.querySelector(".loader-container")!,
            props: { size: "small" }
        });

        await onclick(e);
        unmount(loader);
        dropdownItem.classList.remove("disabled");
    }

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    bind:this={dropdownItem}
    role="button"
    class={combine("dropdown-item", additionalClass)}
    {...restAttributes}
    onclick={makeAnAction}
>
    <div class="loader-container"></div>
    <div class="dropdown-item-content">
        {@render children()}
    </div>
</div>

<style>
    :global {
        .dropdown-item {
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all var(--transition-fast) var(--ease-default);
            font-size: var(--font-size-sm);
            display: flex;
            align-items: center;
            justify-content: left;
            text-align: left!important;
            padding: var(--spacing-xs) var(--spacing-sm);

            & .dropdown-item-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: 100%;
            }

            &:has(.loader-container:has(*)) .dropdown-item-content {
                width: 90%;
            }

            & .loader-container {
                width: 10%;
                margin-right: var(--spacing-sm);
            }

            & .loader-container:not(:has(*)) {
                visibility: hidden;
                width: 0%;
                margin: 0;
            }

            &:has(.dropdown-container) {
                padding: var(--spacing-2xs) var(--spacing-sm)!important;
                padding-right: var(--spacing-xs)!important;
            }

            &[disabled],
            &.disabled {
                cursor:not-allowed!important;
                pointer-events: none;
                filter: brightness(0.7);
            }

            &:hover,
            &.hover {
                background-color: var(--color-hover);
            }
        }
    }
</style>
