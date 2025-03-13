<script module lang="ts">
    import { display, destroy } from "./Component.svelte";
    import { type Snippet } from "svelte";

    let componentContainer: HTMLElement;
    let isMounted = $state(false);
    export function showThis(component: any, props?: any) {
        isMounted = true;
        display(component, componentContainer, props);
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

<div class="layout-container" bind:this={componentContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>

<style>
    .layout-container{
        height:100vh;
    }
</style>
