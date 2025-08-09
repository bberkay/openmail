import Toast from "./Toast.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";

let mountedToasts: Record<string, Record<string, any>> = {};

export interface Props {
    content: string;
    autoCloseDelay?: number;
    onUndo?: (((e: Event) => void) | ((e: Event) => Promise<void>));
    [attribute: string]: unknown;
}

export function show(props: Props) {
    const mountId = generateRandomId();
    const mountedToast = mount(Toast, {
        target: document.getElementById("toast-container")!,
        props: {
            ...props,
            id: mountId,
        }
    });
    mountedToasts[mountId] = mountedToast;
}

export function close(mountId: string) {
    if (Object.hasOwn(mountedToasts, mountId)) {
        unmount(mountedToasts[mountId]);
        delete mountedToasts[mountId];
    }
}
