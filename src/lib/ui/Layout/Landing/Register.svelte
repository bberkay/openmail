<script module lang="ts">
    import { display, destroy } from "../Section.svelte";
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
