import Confirm from "./Confirm.svelte";
import { mount, unmount } from "svelte";

let mountedConfirm: Record<string, any> | null = null;

export interface Props {
    title: string;
    onConfirmText: string;
    onConfirm: (((e: Event) => void) | ((e: Event) => Promise<void>));
    details?: string;
    onCancelText?: string;
    onCancel?: (((e: Event) => void) | ((e: Event) => Promise<void>));
    [attribute: string]: unknown;
}

export function show(props: Props) {
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
