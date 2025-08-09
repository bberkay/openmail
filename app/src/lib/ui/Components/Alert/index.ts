import Alert from "./Alert.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";

type AlertType = "error" | "warning" | "info" | "success";

export interface Props {
    content: string;
    type: AlertType;
    closeable?: boolean;
    details?: string;
    onManage?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
    onManageText?: string;
    [attribute: string]: unknown;
}

let mountedAlerts: Record<string, Record<string, any>> = {};
export function show(
    target: string | HTMLElement,
    props: Props
) {
    const mountId = generateRandomId();
    const mountedAlert = mount(Alert, {
        target:
            typeof target === "string"
                ? document.getElementById(target)!
                : target,
        props: {
            ...props,
            id: mountId,
        },
    });
    mountedAlerts[mountId] = mountedAlert;
}

export function close(mountId: string) {
    if (Object.hasOwn(mountedAlerts, mountId)) {
        unmount(mountedAlerts[mountId]);
        delete mountedAlerts[mountId];
    }
}
