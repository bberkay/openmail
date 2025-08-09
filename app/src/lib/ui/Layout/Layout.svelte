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
    import Titlebar from "./Titlebar.svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<Titlebar/>

<div class="layout-container" bind:this={sectionContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>

<style>
    :global {
        .layout-container{
            height: 100vh;
            padding: 0 var(--spacing-lg);
            padding-top: var(--spacing-2xl);
            border: 1px solid var(--color-border);
            border-radius: var(--titlebar-radius);
        }

        .alert-container {
            display: flex;
            flex-direction: column reverse;
            margin-bottom: var(--spacing-md);

            &:not(:has(div.alert)) {
                visibility: hidden;
                height: 0;
                margin: 0;
            }
        }
    }
</style>
