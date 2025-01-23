<script module lang="ts">
    import { closeSkeleton, showSkeleton } from "$lib/components/Skeleton.svelte";
    import { type Snippet } from "svelte";

    let componentContainer: HTMLElement;
    let isMounted = $state(false);
    export function show(component: any, props?: any) {
        isMounted = true;
        showSkeleton(component, componentContainer, props);
    }

    export function goBack() {
        closeSkeleton();
        isMounted = false;
    }
</script>

<script lang="ts">
    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<div bind:this={componentContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</div>
