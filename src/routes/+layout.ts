import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
import { sharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { LayoutLoad } from './$types';
import { ApiService, GetRoutes, type Response } from "$lib/services/ApiService";

const SERVER_CONNECTION_TIMEOUT = 1000 * 2; // 2 seconds
const SERVER_CONNECTION_TRY_COUNT = 5;

/**
 * Load the accounts from the server
 * and set them in the shared store
 */
async function loadAccounts() {
    if(!sharedStore.server)
        return;

    const response: Response = await ApiService.get(sharedStore.server, GetRoutes.GET_EMAIL_ACCOUNTS);
    sharedStore.accounts = response.data;
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
    if (sharedStore.server) {
        return;
    }

    let serverConnectionTryCount = 0;

    const checkUrlAndLoadAccounts = async (url: string) => {
        try {
            if (serverConnectionTryCount > SERVER_CONNECTION_TRY_COUNT) {
                error(500, "There was an error while connecting to the server!");
            }

            serverConnectionTryCount++;
            const response: Response = await ApiService.get(url, GetRoutes.HELLO);
            if (response.success) {
                sharedStore.server = url;
                loadAccounts();
            } else {
                error(500, response.message);
            }
            return;
        } catch {
            setTimeout(async () => {
                await checkUrlAndLoadAccounts(url);
            }, SERVER_CONNECTION_TIMEOUT);
        }
    }

    await invoke(TauriCommand.GET_SERVER_URL).then(async (url) => {
        await checkUrlAndLoadAccounts(url as string);
    }).catch(async () => {
        error(500, "Error while getting server url!");
    })
}


export const load: LayoutLoad = async ({}) => {
    await connectToLocalServer();
};


// Tauri doesn't have a Node.js server to do proper SSR
// so we will use adapter-static to prerender the app (SSG)
// See: https://beta.tauri.app/start/frontend/sveltekit/ for more info
export const prerender = true;
export const ssr = false;
