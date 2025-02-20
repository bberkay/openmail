import { invoke } from "@tauri-apps/api/core";
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from '@tauri-apps/plugin-notification';
import { TauriCommand, type Email, type OpenMailTaskResults } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { PageLoad } from './$types';
import { ApiService, GetRoutes } from "$lib/services/ApiService";
import { AccountController } from "$lib/controllers/AccountController";

/**
 * Constants
 */
const SERVER_CONNECTION_TRY_SLEEP = 1000 * 2; // 2 seconds

/**
 * Load the accounts from the server
 * and set them in the shared store
 */
async function loadAccounts() {
    if(!SharedStore.server)
        return;

    const accountController = new AccountController();
    const response = await accountController.init();
    if (!response.success) {
        error(500, response.message);
    }
}

/**
 * Create WebSocket connections
 * for every account to receive
 * new email notifications.
 */
async function listenForNotifications() {
    const ws = new WebSocket(
        SharedStore.server.replace("http", "ws") + `/notifications/${SharedStore.accounts.join(",")}`
    );

    let permissionGranted = false;
    ws.onopen = async () => {
        permissionGranted = await isPermissionGranted();
        if (!permissionGranted) {
          const permission = await requestPermission();
          permissionGranted = permission === 'granted';
        }
    }

    ws.onmessage = (e: MessageEvent) => {
        // Send app notification.
        if (permissionGranted) {
            sendNotification({
                title: 'New Email Received!',
                body: 'Here, look at your new email.'
            });
        }

        (e.data as OpenMailTaskResults<Email[]>).forEach((account) => {
            // Add uid of the email to the recent emails store.
            const currentRecentEmails = SharedStore.recentEmails.find(
                current => current.email_address === account.email_address
            );
            if (currentRecentEmails) {
                currentRecentEmails.result = currentRecentEmails.result.concat(
                    account.result.map(email => email.uid)
                );
            }

            // Add email itself to account's mailbox.
            const currentMailbox = SharedStore.mailboxes.find(
                current => current.email_address === account.email_address
            );
            if (currentMailbox) {
                currentMailbox.result.emails = currentMailbox.result.emails.concat(account.result);
            }
        })
    }

    ws.onclose = (e: CloseEvent) => {
        if(e.reason && e.reason.toLowerCase().includes("error")) {
            alert(e.reason);
        }
    }
}

/**
 * Get the server url from the tauri app and
 * check if the server is running. If it is,
 * then set the server url in the shared store and
 * load the accounts. If not, then wait
 * `SERVER_CONNECTION_TIMEOUT` seconds and try
 * again max `SERVER_CONNECTION_TRY_COUNT` times.
 */
async function connectToLocalServer(): Promise<void> {
    if (SharedStore.server) {
        return;
    }

    const checkUrlAndLoadAccounts = async (url: string) => {
        const response = await ApiService.get<GetRoutes.HELLO>(url, GetRoutes.HELLO);
        if (response.success) {
            SharedStore.server = url;
            await loadAccounts();
            await listenForNotifications();
        } else {
            error(500, response.message);
        }
        return;
    }

    await invoke<string>(TauriCommand.GET_SERVER_URL).then(async (url) => {
        await checkUrlAndLoadAccounts(url);
    }).catch(() => {
        setTimeout(async () => {
            await connectToLocalServer();
        }, SERVER_CONNECTION_TRY_SLEEP);
    })
}


export const load: PageLoad = async ({}) => {
    await connectToLocalServer();
};
