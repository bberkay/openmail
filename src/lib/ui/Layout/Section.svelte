<script module lang="ts">
    import { mount, unmount } from "svelte";

    let currentDisplayingSection: Record<string, any> | null = null;

    export function display(section: any, target: HTMLElement, props?: any) {
        destroy();

        currentDisplayingSection = mount(section, {
            target: target,
            props: props
        });
    }

    export function destroy() {
        if (currentDisplayingSection) {
            unmount(currentDisplayingSection);
        }
    }
</script>
