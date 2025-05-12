<script module lang="ts">
    import { display, destroy } from "./Section.svelte";
    import { type Snippet } from "svelte";

    let sectionContainer: HTMLElement;
    let isMounted = $state(false);
    export function showThis(section: any, props?: any) {
        isMounted = true;
        display(section, sectionContainer, props);
    }

    export function backToDefault() {
        destroy();
        isMounted = false;
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
            margin-top: var(--spacing-xs);
            height: calc(100vh - var(--titlebar-height));
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
