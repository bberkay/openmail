<script module lang="ts">
    import { mount, unmount } from "svelte";
    import { type Snippet } from "svelte";

    let sectionContainer: HTMLElement;
    let isMounted = $state(false);
    let currentMount: Record<string, any> | null = null;

    export function showThis(section: any, props?: any) {
        isMounted = true;
        clear();
        currentMount = mount(section, {
            target: sectionContainer,
            props: props
        });
    }

    export function backToDefault() {
        clear();
        isMounted = false;
    }

    function clear() {
        if (currentMount) unmount(currentMount);
        currentMount = null;
    }
</script>

<script lang="ts">
    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<section class="register-container" bind:this={sectionContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</section>

<style>
    :global {
        .register-container {
            margin-top: var(--spacing-2xl);
        }
    }
</style>
