<script module lang="ts">
    import { mount, unmount } from 'svelte';
    import type { Component } from "svelte";

    let mountedModal: Record<string, any> | null;
	let close = () => {
        if (mountedModal) {
            unmount(mountedModal);
            mountedModal = null;
        }
	};

	export function showModal(modal: Component, modalProps: any) {
	    if(mountedModal)
			return;

		mountedModal = mount(modal, {
			target: document.getElementById('modal-container')!,
			props: modalProps
		});
	}
</script>

<script lang="ts">
    import { onMount } from "svelte";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
    }

    let { children }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });
</script>

<div class="backdrop"></div>
<div class="modal">
    {@render children()}
    <button type="button" onclick={close}>Close</button>
</div>

<style>
    .backdrop{
        display:none;
        position: absolute;
        overflow:hidden;
        width:100%;
        height:100%;
        background-color: #000;
        opacity:0.5;
        z-index:99;
        pointer-events: none;
        user-select:none;
    }

    :global(body:has(.backdrop)){
        overflow:hidden;

        & #layout-container {
            pointer-events: none;
        }

        & .overlay{
            display: block;
        }
    }

    .modal {
        background-color: #2e2e2e;
        border:1px solid #5a5a5a;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 5px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index:99999;
    }
</style>
