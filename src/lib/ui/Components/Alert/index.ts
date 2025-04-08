import Alert from "./Alert.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";

export type AlertType = "error" | "warning " | "info" | "success";

let mountedAlerts: Record<string, Record<string, any>> = {};
export function show(
    target: string | HTMLElement,
    props: {
        content: string,
        type: AlertType,
        closeable?: boolean,
        details?: string,
        onManage?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        onManageText?: string,
    }
) {
    const alertId = generateRandomId();
    const mountedAlert = mount(Alert, {
        target:
            typeof target === "string"
                ? document.getElementById(target)!
                : target,
        props: {
            id: alertId,
            ...props
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
