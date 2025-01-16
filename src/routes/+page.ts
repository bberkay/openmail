import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
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
    const response = await accountController.list();
    if (response.success && response.data) {
        SharedStore.accounts = response.data;
    } else {
        error(500, response.message);
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
