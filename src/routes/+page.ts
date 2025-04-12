import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { PageLoad } from './$types';
import { ApiService, GetRoutes } from "$lib/services/ApiService";
import { SERVER_CONNECTION_TRY_SLEEP_MS } from "$lib/constants";

/**
 * Get the server url from the tauri app and
 * check if the server is running.
 */
async function connectToLocalServer(): Promise<void> {
    if (SharedStore.server) {
        return;
    }

    const verifyAndSetServer = async (url: string) => {
        const response = await ApiService.get<GetRoutes.HELLO>(url, GetRoutes.HELLO);
        if (response.success) {
            SharedStore.server = url;
        } else {
            error(500, response.message);
        }
        return;
    }

    await invoke<string>(TauriCommand.GET_SERVER_URL).then(async (url) => {
        await verifyAndSetServer(url);
    }).catch(() => {
        setTimeout(async () => {
            await connectToLocalServer();
        }, SERVER_CONNECTION_TRY_SLEEP_MS);
    })
}


export const load: PageLoad = async ({}) => {
    await connectToLocalServer();
};
