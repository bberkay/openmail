import Toast from "./Toast.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";

let mountedToasts: Record<string, Record<string, any>> = {};

export function show(
    content: string,
    autoCloseDelay?: number,
    onUndo?: (e: Event) => void,
) {
    const toastId = generateRandomId();
    const mountedToast = mount(Toast, {
        target: document.getElementById("toast-container")!,
        props: {
            id: toastId,
            content,
            autoCloseDelay,
            onUndo,
        },
    });
    mountedToasts[toastId] = mountedToast;
}

export function close(toastId: string) {
    if (Object.hasOwn(mountedToasts, toastId)) {
        unmount(mountedToasts[toastId]);
        delete mountedToasts[toastId];
    }
}
