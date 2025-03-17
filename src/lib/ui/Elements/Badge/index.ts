import Badge from "./Badge.svelte";
import { mount, unmount } from "svelte";
import { generateRandomId } from "$lib/utils";
import Icon from "$lib/ui/Elements/Icon";

let mountedBadges: Record<string, Record<string, any>> = {};

export function show(
    target: string | HTMLElement,
    props: {
        content: string,
        lefticon?: Icon,
        righticon?: Icon,
        removeable?: boolean,
        [attribute: string]: unknown
    }
) {
    const badgeId = generateRandomId();
    const mountedBadge = mount(Badge, {
        target:
            typeof target === "string"
                ? document.getElementById(target)!
                : target,
        props: {
            id: badgeId,
            ...props
        }
    });
    mountedBadges[badgeId] = mountedBadge;
}

export function close(badgeId: string) {
    if (Object.hasOwn(mountedBadges, badgeId)) {
        unmount(mountedBadges[badgeId]);
        delete mountedBadges[badgeId];
    }
}
