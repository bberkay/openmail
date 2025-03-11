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

<section class="landing-container" bind:this={componentContainer}>
    <div class="landing-header">
        <h1 class="title">Openmail</h1>
        <p class="subtitle">Secure and Fast Email Communication</p>
    </div>
    <div class="landing-body">
        {#if !isMounted}
            {@render children()}
        {/if}
    </div>
</section>

<style>
    .landing-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        max-width: 37px;

        & .landing-header {
            text-align: center;
        }
    }
</style>
