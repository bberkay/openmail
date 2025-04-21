<script lang="ts">
    import { onMount } from "svelte";
    import "$lib/assets/css/style.css";
    import * as Modal from "$lib/ui/Components/Modal";
    import Layout from "$lib/ui/Layout/Layout.svelte";
    import Variables from "$lib/ui/Layout/Developer/Variables.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";

    let { children } = $props();

    const handleShortcuts = (e: KeyboardEvent) => {
        if (e.ctrlKey && e.code === "Space") {
            e.preventDefault();
            Modal.show(Variables);
        }
    };

    onMount(() => {
        applyInitialTheme();
        applyInitialLanguage();
    });

    $effect(() => {
        if (SharedStore.preferences.theme) {
            applyInitialTheme();
        }

        if (SharedStore.preferences.language) {
            applyInitialLanguage();
        }
    })

    async function applyInitialTheme() {
        document.body.setAttribute("data-color-scheme", SharedStore.preferences.theme);
    }

    async function applyInitialLanguage() {
        document.documentElement.setAttribute("lang", SharedStore.preferences.language);
    }
</script>

<svelte:window onkeydown={handleShortcuts} />

<Layout>
    {@render children()}
</Layout>

<div class="modal-container"></div>
<div class="toast-container"></div>

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
