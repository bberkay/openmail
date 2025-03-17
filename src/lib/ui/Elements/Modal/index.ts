import Modal from "./Modal.svelte";
import { mount, unmount } from "svelte";
import type { Component } from "svelte";

let mountedModal: Record<string, any> | null = null;

export function show(modal: Component, props?: any) {
    if (mountedModal) return;

    mountedModal = mount(modal, {
        target: document.getElementById("modal-container")!,
        props: props,
    });
}

export function close() {
    if (mountedModal) {
        unmount(mountedModal);
        mountedModal = null;
    }
}

export default Modal;
