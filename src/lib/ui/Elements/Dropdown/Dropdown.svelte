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
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div class="dropdown-container" bind:this={dropdownContainer}>
    <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
    <div class="dropdown-toggle-container" onclick={() => { isContentShown = !isContentShown }}>
        {@render children()}
    </div>
    {#if isContentShown}
        <div class="dropdown-content">
            {@render content()}
        </div>
    {/if}
</div>

<style>
    .dropdown-content {
        position: absolute;
        display: flex;
        background-color: #f3f3f3;
        color: #000;
        flex-direction: column;
        padding: 1px;
        border: 1px solid #c2c2c2;
        border-radius: 5px;
        right: -80px;
        top: 30px;
        z-index: 99;
        width: 100px;
    }
</style>
