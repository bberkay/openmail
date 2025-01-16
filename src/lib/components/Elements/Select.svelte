<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        id: string;
        options: string[];
        enableSearch: boolean;
    }

    let { id, options, enableSearch }: Props = $props();

    let isOpen = $state(false);
    let showClass = $derived(isOpen ? "open" : "");
    let filteredOptions: string[] = $state(options);
    let selectedOption: string | null = $state(null);
    let searchInput: HTMLInputElement | null = null;

    onMount(() => {
        const selectWrapper = document.getElementById(id) as HTMLDivElement;
        searchInput = enableSearch ? selectWrapper.querySelector(".search-input") as HTMLInputElement : null;

        document.addEventListener("click", (e) => {
            if (!selectWrapper.contains(e.target as HTMLElement)) {
                closeSelect();
            }
        });

        renderOptions();
    });

    $effect(() => {
        if (isOpen) {
            openSelect();
        } else {
            closeSelect();
        }
    })

    function renderOptions(newOptions: string[] | null = null) {
        filteredOptions = newOptions || options;
    }

    const openSelect = () => {
        isOpen = true;
        if(enableSearch) searchInput!.focus();
    };

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
        selectedOption = value || null;
        closeSelect();
    };

    const handleSearch = (e: Event) => {
        if(!e.target)
            return;

        const target = e.target as HTMLInputElement;
        const searchTerm = target.value;
        renderOptions(options.filter((option) =>
            option.toLowerCase().includes(searchTerm.toLowerCase()),
        ));
    }
</script>

<div class="custom-select-wrapper">
    <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
    <div class="custom-select {showClass}" onclick={() => { isOpen = !isOpen }}>
        <div class="select-trigger">
            <span>{selectedOption}</span>
            <div class="arrow"></div>
        </div>
    </div>
    <div class="options-container {showClass}">
        {#if enableSearch}
            <div class="search-box">
                <input type="text" class="search-input" placeholder="Search..." onclick={(e) => { e.stopPropagation() }} oninput={handleSearch}/>
            </div>
        {/if}
        <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
        <div class="options-list" onclick={selectOption}>
            {#each filteredOptions as option}
                <div class="option ${selectedOption === option ? "selected" : ""}" data-value="${option}">
                    ${option}
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

        .select-trigger {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #333;

            & .arrow {
                border-style: solid;
                border-width: 5px 5px 0 5px;
                border-color: #999 transparent transparent transparent;
                transition: transform 0.3s ease;
            }
        }

        .options-container {
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

        .option {
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
        .search-box {
            padding: 8px;
            position: sticky;
            top: 0;
            background: white;
            border-bottom: 1px solid #e1e1e1;
        }

        .search-input {
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
        .no-results {
            padding: 10px;
            color: #666;
            text-align: center;
            font-style: italic;
        }
    }
</style>
