<script lang="ts">
    import "$lib/assets/css/style.css";
    import Layout from "$lib/ui/Layout/Layout.svelte";
    import Loading from "$lib/ui/Layout/Loading.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { convertToRFC5646Format, getEnumKeyByValue } from "$lib/utils";

    let { children } = $props();

    let isAppLoaded = $derived(SharedStore.isAppLoaded);

    /* TODO: Remove this later */
    const handleShortcuts = (e: KeyboardEvent) => {
        if (e.ctrlKey && e.code === "Space") {
            e.preventDefault();
            showMessage({
                title: "Variables",
                details: `<pre>${JSON.stringify(SharedStore, null, 4)}</pre>`
            });
        }
    };

    $effect(() => {
        if (SharedStore.isAppLoaded) {
            console.log("app loaded");
            if (SharedStore.preferences.theme)
                applyInitialTheme();
            if (SharedStore.preferences.language)
                applyInitialLanguage();
        }
    });

    async function applyInitialTheme() {
        document.body.setAttribute(
            "data-color-scheme",
            SharedStore.preferences.theme.toLowerCase(),
        );
    }

    async function applyInitialLanguage() {
        document.documentElement.setAttribute(
            "lang",
            convertToRFC5646Format(
                getEnumKeyByValue(Language, SharedStore.preferences.language)!,
            ),
        );
    }
</script>

<svelte:window onkeydown={handleShortcuts} />

<Layout>
    {#if !isAppLoaded}
        <Loading />
    {:else}
        {@render children()}
    {/if}
</Layout>

<div class="modal-container" id="modal-container"></div>
<div class="toast-container" id="toast-container"></div>

<style>
    .modal-container {
        position: fixed;
        display: none;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        overflow: hidden;
        top: 0;
        left: 0;
        background-color: #00000099;
        z-index: var(--z-index-overlay);
    }

    .toast-container {
        position: fixed;
        bottom: var(--spacing-lg);
        left: var(--spacing-lg);
        display: flex;
        flex-direction: column-reverse;
        gap: var(--spacing-xs);
    }
</style>
