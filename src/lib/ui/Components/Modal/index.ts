import Modal from "./Modal.svelte";
import { mount, unmount } from "svelte";
import type { Component, ComponentProps } from "svelte";

let mountedModal: Record<string, any> | null = null;

export function show<T extends Component<any>>(modal: T, props?: ComponentProps<T>) {
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
