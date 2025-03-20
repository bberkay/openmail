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
    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<section class="landing-container" bind:this={sectionContainer}>
    <div class="landing-header">
        <h1 class="landing-title">Openmail</h1>
        <p class="landing-subtitle">Secure and Fast Email Communication</p>
    </div>
    <div class="landing-body">
        {#if !isMounted}
            {@render children()}
        {/if}
    </div>
</section>

<style>
    .landing-container {
        width: 100%;
        max-width: var(--container-sm);

        & .landing-header {
            text-align: center;

            .landing-title {
                margin-bottom: var(--spacing-xs);
                font-size: var(--font-size-2xl);
                font-weight: var(--font-weight-bold);
                text-align: center;
                color: var(--color-text-primary);
            }

            .landing-subtitle {
                margin-bottom: var(--spacing-xl);
                font-size: var(--font-size-sm);
                text-align: center;
                color: var(--color-text-secondary);
            }
        }

        & .landing-body-footer {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-lg);
            text-align: center;
            margin-top: var(--spacing-lg);
        }
    }
</style>
