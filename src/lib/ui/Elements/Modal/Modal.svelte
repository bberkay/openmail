<script lang="ts">
    import { onMount } from "svelte";
    import type { Snippet } from "svelte";
    import { close } from "./index";
    import { createDomElement } from "$lib/utils";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();
    let modal: HTMLElement;
    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;

        let closeButton = modal.querySelector("button[data-modal-close]");
        if (!closeButton) {
            closeButton = createDomElement(
                `<button type="button" data-modal-close>Close</button>`,
            );
            modal.appendChild(closeButton);
        }
        closeButton.addEventListener("click", close);
    });
</script>

<div class="modal" bind:this={modal}>
    {@render children()}
</div>

<style>
    .modal {
        background-color: #2e2e2e;
        border: 1px solid #5a5a5a;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 5px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 99999;
    }
</style>
