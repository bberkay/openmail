import { invoke } from "@tauri-apps/api/core";
import type { Response } from "$lib/types";
import { sharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

const SERVER_CONNECTION_TIMEOUT = 1000 * 2; // 2 seconds
const SERVER_CONNECTION_TRY_COUNT = 5;

/**
 * Get the server url from the tauri app and
 * check if the server is running. If it is,
 * then set the server url in the shared store.
 * If not, then wait `SERVER_CONNECTION_TIMEOUT` seconds
 * and try again max `SERVER_CONNECTION_TRY_COUNT` times
 */
async function initServerUrl(): Promise<void> {
    let serverConnectionTryCount = 0;
    if (serverConnectionTryCount > SERVER_CONNECTION_TRY_COUNT) {
        error(500, "There was an error while connecting to the server!");
    }

    const getHelloMessageAndSetUrl = async (url: string) => {
        try {
            serverConnectionTryCount++;
            const response: Response = await fetch(`${url}/hello`).then((res) =>
                res.json()
            );
            if (response.success) {
                sharedStore.server = url;
            } else {
                error(500, response.message);
            }
            return;
        } catch {
            setTimeout(async () => {
                await getHelloMessageAndSetUrl(url);
            }, SERVER_CONNECTION_TIMEOUT);
        }
    }

    await invoke("get_server_url").then(async (url) => {
        await getHelloMessageAndSetUrl(url as string);
    }).catch(async () => {
        error(500, "Error while getting server url!");
    })
}

export const load: PageLoad = async ({}) => {
    await initServerUrl();
};
