<script lang="ts">
    import { slide } from "svelte/transition";
    import { mount, unmount, type Snippet } from "svelte";
    import Icon from "$lib/ui/Components/Icon";

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
        margin-bottom: var(--spacing-sm);
        overflow: hidden;

        & .collapse-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-sm) var(--spacing-md);
            cursor: pointer;
            user-select: none;
        }

        & .collapse-content {
            padding: var(--spacing-md);
        }

        & .collapse-icon {
            transition: transform var(--transition-normal) var(--ease-default);
        }

        & .collapse-icon.open {
            transform: rotate(180deg);
        }
    }
</style>
