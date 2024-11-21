import { invoke } from "@tauri-apps/api/core";
import type { Response } from "$lib/types";
import { sharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

/**
 * 
 */
async function initServer(): Promise<void> {
    let serverConnectionTryCount = 0;
    if (serverConnectionTryCount > 5) {
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
            }, 2000);
        }
    }

    await invoke("get_server_url").then(async (url) => {
        await getHelloMessageAndSetUrl(url as string);
    }).catch(async () => {
        error(500, "Error while getting server url!");
    })
}

export const load: PageLoad = async ({}) => {
    await initServer();
};
