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

<div class="content" bind:this={sectionContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>

<style>
    :global {
        .content {
            width: 80%;
            margin-top: var(--spacing-xl);

            &:has(.compose) {
                width: 50%;
            }

            &:has(.email) {
                width: 70%;
            }
        }
    }
</style>
