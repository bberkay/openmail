<script lang="ts">
    import { onMount, type Snippet } from "svelte";
    import { combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import { getNoMatchFoundTemplate } from "$lib/templates";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        children: Snippet;
        id?: string;
        placeholder?: string;
        value?: string;
        onchange?: (((selectedOption: string) => void) | ((selectedOption: string) => Promise<void>));
        enableSearch?: boolean;
        searchAlgorithm?: ((option: HTMLElement) => boolean);
        resetAfterSelect?: boolean;
        disableClearButton?: boolean;
        disabled?: boolean;
        [attribute: string]: unknown;
    }

    let {
        children,
        id,
        placeholder,
        value,
        onchange,
        enableSearch,
        searchAlgorithm,
        resetAfterSelect,
        disableClearButton,
        disabled,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let isOpen = $state(false);
    let options: HTMLElement[] = $state([]);
    let selectedOption: HTMLElement | null = $state(null);
    const defaultValue = value;
    const isInitializedAsDisabled = disabled;
    disableClearButton = isInitializedAsDisabled;

    let selectWrapper: HTMLElement;
    let optionsList: HTMLElement;
    let searchInput: HTMLInputElement;

    onMount(() => {
        searchInput = selectWrapper.querySelector(".search-input")!;
        options = Array.from(selectWrapper.querySelectorAll(".option")) as HTMLElement[];
        if (value) selectOption(value, true)
        filterOptions();
    });

    function filterOptions(searchTerm: string | null = null) {
        searchTerm = searchTerm?.toLowerCase() || null;

        let isAnyOptionFound = false;
        optionsList.querySelector(".no-results")?.remove();

        options.forEach((option: HTMLElement) => {
            const optionValue = option.getAttribute("data-value")!.toString().toLowerCase();
            const optionContent = option.innerText!.toString().toLowerCase()
            if (searchTerm) {
                const isOptionIncludesSearchTerm = optionValue.includes(searchTerm) || optionContent.includes(searchTerm);
                const isOptionConfirmSearchAlgorithm = (!searchAlgorithm || searchAlgorithm(option))
                if (isOptionIncludesSearchTerm && isOptionConfirmSearchAlgorithm) {
                    option.classList.remove("invisible");
                    isAnyOptionFound = true;
                } else {
                    option.classList.add("invisible");
                }
            } else {
                option.classList.remove("invisible");
            }
        })

        if(searchTerm && !isAnyOptionFound) {
            optionsList.innerHTML += getNoMatchFoundTemplate();
        }
    }

    async function selectOption(
        value: string,
        disableCallback: boolean = false,
        resetToDefault: boolean = false
    ) {
        disabled = true;
        if(selectedOption) selectedOption.classList.remove("selected");
        selectedOption = options.find(option => option.dataset.value == value)!;
        selectedOption.classList.add("selected");
        if(onchange && !disableCallback) await onchange(value.toString());
        if (!isInitializedAsDisabled) disabled = false;
        if(resetAfterSelect && !resetToDefault) clearSelection();
        closeSelect();
    }

    function closeSelect() {
        if (!isOpen)
            return;

        isOpen = false;
        if(enableSearch) searchInput!.value = "";
        filterOptions();
    }

    const closeWhenClickedOutside = (e: Event) => {
        if (isOpen && !selectWrapper.contains(e.target as HTMLElement)) {
            closeSelect();
        }
    }

    const toggleSelect = () => {
        if (isOpen)
            return closeSelect();

        isOpen = true;
        if (enableSearch) searchInput!.focus();
    }

    const handleSelection = async (e: Event) => {
        if (!e.target)
            return;

        const option = (e.target as HTMLDivElement).closest<HTMLElement>(".option")!
        if (!option)
            return;

        const value = option.dataset.value;
        if(!value)
            return;

        await selectOption(value);
    };

    const handleSearch = (e: Event) => {
        if(!e.target)
            return;

        const target = e.target as HTMLInputElement;
        filterOptions(target.value);
    }

    const clearSelection = () => {
        if (disabled)
            return;

        if (defaultValue) {
            selectOption(defaultValue, false, true);
        } else {
            selectedOption = null;
            optionsList.querySelector(".selected")?.classList.remove("selected");
            filterOptions();
        }
    }
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={selectWrapper}
    class={combine("custom-select-wrapper", additionalClass)}
    {...restAttributes}
>
    <div
        id={id}
        class="custom-select {isOpen ? "visible" : ""} {disabled ? "disabled" : ""}"
        onclick={!disabled ? toggleSelect : () => {}}
        onkeydown={(e) => !disabled && e.key === "Enter" && toggleSelect()}
        tabindex="0"
        role="button"
        aria-expanded={isOpen}
    >
        <div class="select-trigger">
            <div class="select-trigger-content">
                {#if selectedOption}
                    <span data-value={selectedOption.getAttribute("data-value")!}>
                        {selectedOption.textContent!.trim()}
                    </span>
                    {#if !disableClearButton}
                        <Button.Basic
                            type="button"
                            class="btn-inline clear-button {selectedOption ? "visible" : ""}"
                            onclick={clearSelection}
                        >
                            <Icon name="close" />
                        </Button.Basic>
                    {/if}
                {:else}
                    <span data-value="">{placeholder}</span>
                {/if}
            </div>
            <Icon name="dropdown" />
        </div>
    </div>
    <div class="options-container {isOpen ? "visible" : ""}">
        {#if enableSearch}
            <div class="search-box">
                <Input.Group>
                    <Icon name="search" />
                    <Input.Basic
                        type="text"
                        class="search-input"
                        style="font-size: var(--font-size-sm)"
                        placeholder={local.search[DEFAULT_LANGUAGE]}
                        onclick={(e: Event) => { e.stopPropagation() }}
                        oninput={handleSearch}
                    />
                </Input.Group>
            </div>
        {/if}
        <div
            class="options-list"
            onclick={handleSelection}
            onkeydown={(e) => e.key === "Enter" && handleSelection(e)}
            tabindex="0"
            role="button"
            aria-expanded={isOpen}
            bind:this={optionsList}
        >
            {@render children()}
        </div>
    </div>
</div>

<style>
    :global {
        .label + .custom-select-wrapper {
            margin-top: var(--spacing-2xs);
        }

        .custom-select-wrapper {
            position: relative;
            width: max-content;
            user-select: none;
            text-align: left;
            font-size: var(--font-size-sm);

            & .custom-select {
                position: relative;
                border: 1px solid var(--color-border);
                border-radius: var(--radius-sm);
                border-bottom-left-radius: none;
                border-bottom-right-radius: none;
                padding: var(--spacing-xs) var(--spacing-sm);
                cursor: pointer;
                background-color: var(--color-bg-primary);

                &.visible {
                    border-color: var(--color-text-primary);
                }

                & .select-trigger {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    color: var(--color-text-primary);

                    & .select-trigger-content {
                        display: flex;
                        align-items: center;
                        gap: var(--spacing-xs);
                        margin-right: var(--spacing-xs);
                        flex: 1;

                        & .clear-button {
                            & svg {
                                width: var(--font-size-sm);
                                height: var(--font-size-sm);
                            }
                        }
                    }
                }
            }

            & .options-container {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--color-bg-primary);
                border: 1px solid var(--color-border);
                border-radius: var(--radius-sm);
                border-top-left-radius: 0!important;
                border-top-right-radius: 0!important;
                max-height: var(--container-sm);
                overflow-y: auto;
                z-index: var(--z-index-dropdown);
                opacity: 0;
                visibility: hidden;
                transition: all var(--transform-fast) var(--ease-default);
                box-shadow: var(--shadow-sm);
                font-size: var(--font-size-sm);

                & .search-box {
                    position: sticky;
                    top: 0;
                    border-bottom: 1px solid var(--color-border-subtle);

                    & .input-group {
                        padding-left: var(--spacing-xs);
                        font-size: var(--font-size-sm);
                    }
                }

                & .no-results {
                    padding: var(--spacing-sm);
                    color: var(--color-text-secondary);
                    text-align: center;
                    font-style: italic;
                }
            }
        }
    }
</style>
