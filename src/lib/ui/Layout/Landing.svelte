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
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
</script>

<section class="landing-container" bind:this={sectionContainer}>
    <div class="landing-header">
        <h1 class="logo">{local.openmail[DEFAULT_LANGUAGE]}</h1>
        <p class="landing-subtitle">
            {local.secure_and_fast_email_client[DEFAULT_LANGUAGE]}
        </p>
    </div>
    <div class="landing-body">
        {#if !isMounted}
            {@render children()}
        {/if}
    </div>
</section>

<style>
    :global {
        .landing-container {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;

            & .landing-header {
                text-align: center;

                .logo {
                    margin-bottom: var(--spacing-xs);
                    text-align: center;
                }

                .landing-subtitle {
                    margin-bottom: var(--spacing-xl);
                    font-size: var(--font-size-sm);
                    text-align: center;
                    color: var(--color-text-secondary);
                }
            }

            & .landing-body {
                width: var(--container-md);
            }

            & .landing-body-footer {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-lg);
                text-align: center;
                margin-top: var(--spacing-2xl);
            }
        }
    }
</style>
