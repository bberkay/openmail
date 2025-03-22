<script lang="ts">
    import { type Snippet } from "svelte";

    interface Props {
        children: Snippet;
        content: Snippet;
    }

    let {
        children,
        content
    }: Props = $props();

    let isContentShown = $state(false);
    let dropdownContainer: HTMLElement;

    const closeWhenClickedOutside = (e: Event) => {
        if(!dropdownContainer.contains(e.target as HTMLElement)) {
            isContentShown = false;
        }
    }

    const toggleDropdown = (e: Event) => {
        e.stopPropagation();
        isContentShown = !isContentShown;
    }
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div class="dropdown-container" bind:this={dropdownContainer}>
    <div
        class="dropdown-toggle-container"
        onclick={toggleDropdown}
        onkeydown={toggleDropdown}
        role="button"
        tabindex="0"
    >
        {@render children()}
    </div>
    {#if isContentShown}
        <div class="dropdown-content">
            {@render content()}
        </div>
    {/if}
</div>

<style>
    :global {
        .dropdown-container {
            position: relative;
            z-index: var(--z-index-dropdown);

            & .dropdown-content {
                position: absolute;
                display: flex;
                background-color: var(--color-border-subtle);
                color: var(--color-text-primary);
                flex-direction: column;
                padding: 1px;
                border: 1px solid var(--color-border);
                border-radius: var(--radius-sm);
                right: -80px;
                top: 30px;
                width: 100px;
            }
        }
    }
</style>
