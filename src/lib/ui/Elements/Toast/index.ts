import Toast from './Toast.svelte';
import { mount, unmount } from 'svelte';
import type { Component } from 'svelte';
import { generateRandomId } from '$lib/utils';

let mountedToasts: Record<string, Record<string, any>> = {};

export function show(notification: string | Component, toastProps: any) {
    const toastId = generateRandomId();

    let content = '';
    if (typeof notification === 'string') {
        content = notification + ' ' + toastId;
        notification = Toast;
    }

    const mountedNotification = mount(notification, {
        target: document.getElementById('notification-container')!,
        props: { ...toastProps, id: toastId },
    });
    mountedToasts[toastId] = mountedNotification;
}

export function close(toastId: string) {
    if (Object.hasOwn(mountedToasts, toastId)) {
        unmount(mountedToasts[toastId]);
        delete mountedToasts[toastId];
    }
}

export { Toast };
