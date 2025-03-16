import Alert from "./Alert.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";

export type AlertType = "error" | "warning " | "info" | "success";

let mountedAlerts: Record<string, Record<string, any>> = {};
export function show(
    targetIdOrElement: string | HTMLElement,
    content: string,
    type: AlertType,
    closeable?: boolean,
) {
    const alertId = generateRandomId();
    const mountedAlert = mount(Alert, {
        target:
            typeof targetIdOrElement === "string"
                ? document.getElementById(targetIdOrElement)!
                : targetIdOrElement,
        props: {
            id: alertId,
            content,
            type,
            closeable,
        },
    });
    mountedAlerts[alertId] = mountedAlert;
}

export function close(alertId: string) {
    if (Object.hasOwn(mountedAlerts, alertId)) {
        unmount(mountedAlerts[alertId]);
        delete mountedAlerts[alertId];
    }
}
