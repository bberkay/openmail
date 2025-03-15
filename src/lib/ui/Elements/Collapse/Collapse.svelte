<script lang="ts">
    import { slide } from "svelte/transition";
    import { mount, unmount, type Snippet } from "svelte";
    import Icon from "$lib/ui/Elements/Icon";

    interface Props {
        title: string;
        children: Snippet;
        openAtStart?: boolean;
        [attribute: string]: unknown;
    }

    let {
        title,
        children,
        openAtStart,
        ...attributes
    }: Props = $props();

    let isOpen = $state(openAtStart ?? false);
    const toggle = () => {
        isOpen = !isOpen;
    };
</script>

<div class="collapse-wrapper" {...attributes}>
    <div
        class="collapse-header"
        onclick={toggle}
        onkeydown={(e) => e.key === "Enter" && toggle()}
        tabindex="0"
        role="button"
        aria-expanded={isOpen}
    >
        <div class="header-content">
            {title}
        </div>
        <div class="collapse-icon {isOpen ? 'open' : ''}">
            <Icon name="collapse" />
        </div>
    </div>

    {#if isOpen}
        <div class="collapse-content" transition:slide={{ duration: 300 }}>
            {@render children()}
        </div>
    {/if}
</div>

<style>
    .collapse-wrapper {
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-bottom: 10px;
        overflow: hidden;
    }

    .collapse-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background-color: #f5f5f5;
        cursor: pointer;
        font-weight: 500;
        user-select: none;
    }

    .collapse-content {
        padding: 16px;
    }

    .collapse-icon {
        transition: transform 0.3s ease;
    }

    .collapse-icon.open {
        transform: rotate(180deg);
    }
</style>
