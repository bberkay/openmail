<script module lang="ts">
    import { mount, unmount, type Component, type Snippet } from "svelte";

    let currentMountedComponent: Record<string, any> | null = null;

    export function showSkeleton(component: any, target: HTMLElement, props?: any) {
        closeSkeleton();

        currentMountedComponent = mount(component, {
            target: target,
            props: props
        });
    }

    export function closeSkeleton() {
        if (currentMountedComponent) {
            unmount(currentMountedComponent);
        }
    }
</script>
