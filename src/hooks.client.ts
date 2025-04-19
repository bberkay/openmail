import type { Handle, ServerInit } from "@sveltejs/kit";
import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes } from "$lib/services/ApiService";
import { SERVER_CONNECTION_TRY_SLEEP_MS } from "$lib/constants";

async function loadPreferences(): Promise<void> {
    const response = await ApiService.get(GetRoutes.GET_PREFERENCES);
    if (response.success && response.data) {
        SharedStore.preferences = response.data;
    }
}

async function loadServerUrl(): Promise<void> {
    if (SharedStore.server) {
        return;
    }

    const serverUrl = await invoke<string>(TauriCommand.GET_SERVER_URL);
    SharedStore.server = serverUrl;
    const response = await ApiService.get(GetRoutes.HELLO);
    if (!response.success) {
        SharedStore.server = "";
    }
}

export const init: ServerInit = () => {
    const connectToLocalServer = async () => {
        await loadServerUrl();
        if (SharedStore.server) {
            await loadPreferences();
        } else {
            setTimeout(async () => {
                await connectToLocalServer();
            }, SERVER_CONNECTION_TRY_SLEEP_MS);
        }
    }

    connectToLocalServer();
}

export const handle: Handle = ({ event, resolve }) => {
    // TODO: Should we wait for the preferences?
    return resolve(event, {
        transformPageChunk: ({ html }) =>
            html
                .replace("%lang%", SharedStore.preferences.language)
                .replace("%data-color-scheme%", SharedStore.preferences.theme),
    });
};
