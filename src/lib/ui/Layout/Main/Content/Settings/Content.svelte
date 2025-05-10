<script module lang="ts">
    import { display, destroy } from "$lib/ui/Layout/Section.svelte";
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
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Form from "$lib/ui/Components/Form";
    import { FileSystem } from "$lib/services/FileSystem";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

    const saveChanges = async (e: Event): Promise<void> => {
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences({
            language: SharedStore.preferences.language,
            theme: SharedStore.preferences.theme,
        });
    };
</script>

<Form onsubmit={saveChanges}>
    <section class="settings-content" bind:this={sectionContainer}>
        {#if !isMounted}
            {@render children()}
        {/if}
    </section>
</Form>

<style>
    :global {
        .settings {
            .settings-content {
                display: flex;
                flex-direction: column;
                width: 100%;
                border: 1px solid var(--color-border-subtle);
                border-radius: var(--radius-sm);
                padding: var(--spacing-lg) var(--spacing-xl);
                font-size: var(--font-size-sm);
                gap: var(--spacing-lg);

                & .settings-content-header {
                    display: flex;
                    flex-direction: column;

                    & .settings-content-title {
                        font-size: var(--font-size-xl);
                    }
                }

                & .settings-content-body {
                    display: flex;
                    flex-direction: column;

                    & .settings-section {
                        display: flex;
                        flex-direction: row;
                        justify-content: space-between;
                        border-top: 1px solid var(--color-border-subtle);
                        padding: var(--spacing-lg) 0;

                        & .settings-section-title {
                            display: flex;
                            flex-direction: column;
                            flex-grow: 1;
                        }

                        & .settings-section-body {
                            flex-grow: 2;
                        }
                    }
                }
            }
        }
    }
</style>
