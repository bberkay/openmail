import Message from "./Message.svelte";
import { mount, unmount } from "svelte";

let mountedMessage: Record<string, any> | null = null;

export interface Props {
    title: string
    details?: string;
    onCloseText?: string;
    onClose?: (((e: Event) => void) | ((e: Event) => Promise<void>));
    [attribute: string]: unknown;
}

export function show(props: Props) {
    if (mountedMessage) return;

    mountedMessage = mount(Message, {
        target: document.getElementById("modal-container")!,
        props: props,
    });
}

export function close() {
    if (mountedMessage) {
        unmount(mountedMessage);
        mountedMessage = null;
    }
}

export default Message;
