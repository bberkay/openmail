<script module lang="ts">
    import { mount, unmount } from "svelte";

    let currentDisplayingComponent: Record<string, any> | null = null;

    export function display(component: any, target: HTMLElement, props?: any) {
        destroy();

        currentDisplayingComponent = mount(component, {
            target: target,
            props: props
        });
    }

    export function destroy() {
        if (currentDisplayingComponent) {
            unmount(currentDisplayingComponent);
        }
    }
</script>
