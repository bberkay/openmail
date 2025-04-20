import type { Handle, ServerInit } from "@sveltejs/kit";
import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes } from "$lib/services/ApiService";
import { DEFAULT_PREFERENCES, SERVER_CONNECTION_TRY_SLEEP_MS } from "$lib/constants";
import { FileSystem } from "$lib/services/FileSystem";

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    SharedStore.preferences = await fileSystem.readPreferences();
    if (!SharedStore.preferences) {
        await fileSystem.savePreferences(DEFAULT_PREFERENCES);
    }
}

async function connectToLocalServer(): Promise<void> {
    const serverUrl = await invoke<string>(TauriCommand.GET_SERVER_URL);
    SharedStore.server = serverUrl;
    const response = await ApiService.get(GetRoutes.HELLO);
    if (!response.success) {
        SharedStore.server = "";
        setTimeout(async () => {
            await connectToLocalServer();
        }, SERVER_CONNECTION_TRY_SLEEP_MS);
    }
}

export const init: ServerInit = async () => {
    connectToLocalServer();
    await initializeFileSystem();
}

export const handle: Handle = async ({ event, resolve }) => {
    if (!SharedStore.preferences) {
        await initializeFileSystem();
    }
    return await resolve(event, {
        transformPageChunk: ({ html }) =>
            html
                .replace("%lang%", SharedStore.preferences.language)
                .replace("%data-color-scheme%", SharedStore.preferences.theme),
    });
};
