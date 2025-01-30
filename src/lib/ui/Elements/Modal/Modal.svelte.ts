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
