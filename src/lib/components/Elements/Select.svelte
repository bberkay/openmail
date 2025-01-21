<script lang="ts">
    import { onDestroy, onMount } from "svelte";

    export type Option = {
        value: string | number,
        inner: string | number
    }

    interface Props {
        options: Option[];
        placeholder?: string;
        value?: Option;
        operation?: (selectedOption: string | null) => void,
        enableSearch?: boolean;
    }

    let {
        options,
        placeholder = undefined,
        value = undefined,
        operation = undefined,
        enableSearch = false,
    }: Props = $props();

    let isOpen = $state(false);
    let filteredOptions: Option[] = $state(options);
    let selectedOption: Option | null = $state(value || null);
    let searchInput: HTMLInputElement | null = null;
    let selectWrapper: HTMLElement;

    onMount(() => {
        if(selectWrapper) {
            searchInput = enableSearch ? selectWrapper.querySelector(".search-input") as HTMLInputElement : null;
            document.removeEventListener("click", closedWhenClickedOutside);
            document.addEventListener("click", closedWhenClickedOutside);
            renderOptions();
        }
    });

    onDestroy(() => {
        document.removeEventListener("click", closedWhenClickedOutside);
    });

    const closedWhenClickedOutside = (e: Event) => {
        if (!selectWrapper.contains(e.target as HTMLElement)) {
            closeSelect();
        }
    }

    $effect(() => {
        if (isOpen && enableSearch) {
            searchInput!.focus();
        }
    })

    $effect(() => {
        selectedOption = value || null;
    });

    function renderOptions(newOptions: Option[] | null = null) {
        filteredOptions = newOptions || options;
    }

    const closeSelect = () => {
        if (!isOpen)
            return;

        isOpen = false;
        if(enableSearch) searchInput!.value = "";
        renderOptions();
    };

    const selectOption = (e: Event) => {
        if (!e.target)
            return;

        const option = (e.target as HTMLDivElement).closest<HTMLElement>(".option")!
        if (!option)
            return;

        const value = option.dataset.value;
        const inner = option.innerText;
        if(!value || !inner)
            return;

        selectedOption = { value, inner };
        if(operation) operation(selectedOption.value.toString());
        closeSelect();
    };

    const handleSearch = (e: Event) => {
        if(!e.target)
            return;

        const target = e.target as HTMLInputElement;
        const searchTerm = target.value;
        renderOptions(options.filter((option) =>
            option.value.toString().toLowerCase().includes(searchTerm.toLowerCase())
            || option.inner.toString().toLowerCase().includes(searchTerm.toLowerCase()),
        ));
    }

    const clearSelection = (e: Event) => {
        selectedOption = null;
        renderOptions();
    }
</script>

<div class="custom-select-wrapper" bind:this={selectWrapper}>
    <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
    <div class="custom-select {isOpen ? "open" : ""}" onclick={() => { isOpen = !isOpen }}>
        <div class="select-trigger">
            <div class="select-trigger-content">
                <span>{selectedOption && selectedOption.value ? selectedOption.inner : placeholder}</span>
                <button class="clear-button {selectedOption ? "visible" : ""}" onclick={clearSelection}>×</button>
            </div>
            <div class="arrow"></div>
        </div>
    </div>
    <div class="options-container {isOpen ? "open" : ""}">
        {#if enableSearch}
            <div class="search-box">
                <input type="text" class="search-input" placeholder="Search..." onclick={(e) => { e.stopPropagation() }} oninput={handleSearch}/>
            </div>
        {/if}
        <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
        <div class="options-list" onclick={selectOption}>
            {#each filteredOptions as option}
                <div class="option ${selectedOption && selectedOption.value === option.value ? "selected" : ""}" data-value="${option.value}">
                    {@html option.inner}
                </div>
            {:else}
                <div class="no-results">No matching options found</div>
            {/each}
        </div>
    </div>
</div>

<style>
    .custom-select-wrapper {
        position: relative;
        width: 300px;
        font-family: Arial, sans-serif;
        user-select: none;

        & .custom-select {
            position: relative;
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            padding: 10px;
            cursor: pointer;
            background-color: white;

            &.open {
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);

                & .arrow {
                    transform: rotate(180deg);
                }
            }
        }

        & .select-trigger {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #333;

            & .select-trigger-content {
                display: flex;
                align-items: center;
                gap: 8px;
                flex: 1;

                & .clear-button {
                    background: none;
                    border: none;
                    color: #999;
                    cursor: pointer;
                    padding: 2px 6px;
                    font-size: 18px;
                    line-height: 1;
                    visibility: hidden;
                    opacity: 0;
                    transition: all 0.2s ease;

                    &.visible{
                        visibility: visible;
                        opacity: 1;
                    }

                    &:hover{
                        color: #666;
                    }
                }
            }

            & .arrow {
                border-style: solid;
                border-width: 5px 5px 0 5px;
                border-color: #999 transparent transparent transparent;
                transition: transform 0.3s ease;
            }
        }

        & .options-container {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            margin-top: 4px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

            &.open{
                opacity: 1;
                visibility: visible;
            }

            /* Custom scrollbar */
            &::-webkit-scrollbar {
                width: 6px;
            }

            &::-webkit-scrollbar-track {
                background: #f1f1f1;
            }

            &::-webkit-scrollbar-thumb {
                background: #ccc;
                border-radius: 3px;
            }

            &::-webkit-scrollbar-thumb:hover {
                background: #999;
            }
        }

        & .option {
            padding: 10px;
            cursor: pointer;
            transition: background-color 0.2s ease;

            &:hover{
                background-color: #f8f9fa;
            }

            &.selected {
                background-color: #e3f2fd;
                color: #007bff;
                font-weight: 500;
            }
        }

        /* Search input styles */
        & .search-box {
            padding: 8px;
            position: sticky;
            top: 0;
            background: white;
            border-bottom: 1px solid #e1e1e1;
        }

        & .search-input {
            width: 100%;
            padding: 6px;
            border: 1px solid #e1e1e1;
            border-radius: 4px;
            outline: none;

            &:focus {
                border-color: #007bff;
            }
        }

        /* No results message */
        & .no-results {
            padding: 10px;
            color: #666;
            text-align: center;
            font-style: italic;
        }
    }
</style>
