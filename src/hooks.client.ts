import type { ClientInit } from "@sveltejs/kit";
import { invoke } from "@tauri-apps/api/core";
import { TauriCommand, type Preferences } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes } from "$lib/services/ApiService";
import { DEFAULT_PREFERENCES, SERVER_CONNECTION_TRY_SLEEP_MS } from "$lib/constants";
import { FileSystem } from "$lib/services/FileSystem";

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    SharedStore.preferences = await fileSystem.readPreferences();
    for (const preference of Object.keys(DEFAULT_PREFERENCES) as (keyof Preferences)[]) {
        if (!Object.hasOwn(SharedStore.preferences, preference)) {
            await fileSystem.savePreferences({ [preference]: DEFAULT_PREFERENCES[preference] });
        }
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

export const init: ClientInit = async () => {
    connectToLocalServer();
    await initializeFileSystem();
}
