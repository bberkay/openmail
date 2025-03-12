import Message from "./Message.svelte";
import { mount, unmount } from "svelte";

let mountedMessage: Record<string, any> | null = null;

export function show(
    content: string,
    onOkText?: string,
    onOk?: (e: Event) => void,
) {
    if (mountedMessage) return;

    mountedMessage = mount(Message, {
        target: document.getElementById("modal-container")!,
        props: { content, onOkText, onOk },
    });
}

export function close() {
    if (mountedMessage) {
        unmount(mountedMessage);
        mountedMessage = null;
    }
}

export default Message;
