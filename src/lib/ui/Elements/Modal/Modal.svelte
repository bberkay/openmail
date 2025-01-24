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

	export function show(modal: Component, modalProps: any) {
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

<div class="modal">
    {@render children()}
    <button type="button" onclick={close}>Close</button>
</div>

<style>
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
