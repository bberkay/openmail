<script module lang="ts">
    import { mount, unmount } from "svelte";

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
