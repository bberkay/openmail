<script lang="ts">
    import { onMount, type Snippet } from "svelte";
    import { combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        children: Snippet;
        id?: string;
        placeholder?: string;
        value?: string;
        onchange?: (selectedOption: string) => void;
        enableSearch?: boolean;
        resetAfterSelect?: boolean;
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
        resetAfterSelect,
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

    let selectWrapper: HTMLElement;
    let optionsList: HTMLElement;
    let searchInput: HTMLInputElement;

    const noResultWarning = `<div class="no-results">No matching options found</div>`;

    onMount(() => {
        searchInput = selectWrapper.querySelector(".search-input")!;
        options = Array.from(selectWrapper.querySelectorAll(".option")) as HTMLElement[];
        if (value) selectOption(value)
        filterOptions();
    });

    function filterOptions(searchTerm: string | null = null) {
        searchTerm = searchTerm?.toLowerCase() || null;

        let isAnyOptionFound = false;
        optionsList.querySelector(".no-results")?.remove();

        options.forEach((option: HTMLElement) => {
            if (searchTerm) {
                if (
                    option.getAttribute("data-value")!.toString().toLowerCase().includes(searchTerm)
                    || option.innerText!.toString().toLowerCase().includes(searchTerm)
                ) {
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
            optionsList.innerHTML += noResultWarning;
        }
    }

    function selectOption(value: string) {
        if(selectedOption) selectedOption.classList.remove("selected");
        selectedOption = options.find(option => option.dataset.value == value)!;
        selectedOption.classList.add("selected");
        if(onchange) onchange(value.toString());
        if(resetAfterSelect) selectedOption = null;
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
        if (!selectWrapper.contains(e.target as HTMLElement)) {
            closeSelect();
        }
    }

    const toggleSelect = () => {
        if (isOpen)
            return closeSelect();

        isOpen = true;
        if (enableSearch) searchInput!.focus();
    }

    const handleSelection = (e: Event) => {
        if (!e.target)
            return;

        const option = (e.target as HTMLDivElement).closest<HTMLElement>(".option")!
        if (!option)
            return;

        const value = option.dataset.value;
        if(!value)
            return;

        selectOption(value);
    };

    const handleSearch = (e: Event) => {
        if(!e.target)
            return;

        const target = e.target as HTMLInputElement;
        filterOptions(target.value);
    }

    const clearSelection = () => {
        selectedOption = null;
        optionsList.querySelector(".selected")?.classList.remove("selected");
        filterOptions();
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
        class="custom-select {isOpen ? "open" : ""} {disabled ? "disabled" : ""}"
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
                        {selectedOption.textContent!.split("#separator#")[0].trim()}
                    </span>
                    <Button.Basic
                        type="button"
                        class="clear-button {selectedOption ? "visible" : ""}"
                        onclick={!disabled ? clearSelection : () => {}}
                    >×</Button.Basic>
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
                        placeholder="Search"
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
        .custom-select-wrapper {
            position: relative;
            width: max-content;
            user-select: none;
            text-align: left;

            & .custom-select {
                position: relative;
                border: 1px solid var(--color-border);
                border-radius: var(--radius-sm);
                border-bottom-left-radius: none;
                border-bottom-right-radius: none;
                padding: var(--spacing-xs) var(--spacing-sm);
                cursor: pointer;
                background-color: var(--color-bg-primary);

                &.open {
                    border-color: var(--color-text-primary);
                }

                &.disabled {
                    cursor: auto;
                    opacity: 0.9;
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
                        flex: 1;

                        & .clear-button {
                            background: none;
                            border: none;
                            color: var(--color-text-secondary);
                            cursor: pointer;
                            padding: calc(var(--spacing-2xs) / 2) calc(var(--spacing-xs) / 2);
                            line-height: 1;
                            visibility: hidden;
                            opacity: 0;
                            transition: all var(--transform-fast) var(--ease-default);

                            &:hover{
                                opacity: 0.7;
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
                border-top-left-radius: none;
                border-top-right-radius: none;
                max-height: var(--container-sm);
                overflow-y: auto;
                z-index: var(--z-index-dropdown);
                opacity: 0;
                visibility: hidden;
                transition: all var(--transform-fast) var(--ease-default);
                box-shadow: var(--shadow-sm);

                & .search-box {
                    position: sticky;
                    top: 0;
                    border-bottom: 1px solid var(--color-border-subtle);
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
