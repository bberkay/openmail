<script module lang="ts">
    import { mount, unmount } from "svelte";
    import { type Snippet } from "svelte";

    let sectionContainer: HTMLElement;
    let isMounted = $state(false);
    let currentMount: Record<string, any> | null = null;

    export function showThis(section: any, props?: any) {
        isMounted = true;
        clear();
        currentMount = mount(section, {
            target: sectionContainer,
            props: props
        });
    }

    export function backToDefault() {
        clear();
        isMounted = false;
    }

    function clear() {
        if (currentMount) unmount(currentMount);
        currentMount = null;
    }
</script>


<script lang="ts">
    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<section class="settings-content" bind:this={sectionContainer}>
    {#if !isMounted}
        {@render children()}
    {/if}
</section>

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
                height: 100%;

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
                    height: 100%;
                    overflow-x: hidden;
                    overflow-y: auto;

                    & .settings-section {
                        display: flex;
                        flex-direction: row;
                        justify-content: space-between;
                        border-top: 1px solid var(--color-border-subtle);
                        padding: var(--spacing-lg) 0;

                        & .settings-section-title {
                            display: flex;
                            flex-direction: column;
                            width: 40%;
                        }

                        & .settings-section-body {
                            width: 60%;
                        }
                    }
                }
            }
        }
    }
</style>
