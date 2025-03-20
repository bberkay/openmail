import Confirm from "./Confirm.svelte";
import { mount, unmount } from "svelte";

let mountedConfirm: Record<string, any> | null = null;

export function show(props: {
    content: string,
    onConfirmText: string,
    onConfirm: (e: Event) => void,
    onCancelText?: string,
    onCancel?: (e: Event) => void,
}) {
    if (mountedConfirm) return;

    mountedConfirm = mount(Confirm, {
        target: document.getElementById("modal-container")!,
        props: props
    });
}

export function close() {
    if (mountedConfirm) {
        unmount(mountedConfirm);
        mountedConfirm = null;
    }
}

export default Confirm;
