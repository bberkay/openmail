import type { ClientInit } from "@sveltejs/kit";
import { invoke } from "@tauri-apps/api/core";
import { TauriCommand } from "$lib/types";
import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService } from "$lib/services/ApiService";
import { FileSystem } from "$lib/services/FileSystem";
import { AccountController } from "$lib/controllers/AccountController";

const SERVER_CONNECTION_TRY_SLEEP_MS = 500;

async function loadAccounts(): Promise<void> {
    if (!SharedStore.server)
        throw new Error("Server must be initialized before loading accounts.");

    await AccountController.init();
}

async function connectToLocalServer(): Promise<void> {
    while (true) {
        await new Promise(resolve => setTimeout(resolve, SERVER_CONNECTION_TRY_SLEEP_MS));
        try {
            const serverUrl = await invoke<string>(TauriCommand.GET_SERVER_URL);
            const response = await ApiService.hello(serverUrl);
            if (response.success) {
                SharedStore.server = serverUrl;
                return;
            }
        } catch {}
    }
}

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    const savedPreferences = await fileSystem.readPreferences();
    SharedStore.preferences = { ...SharedStore.preferences,  ...savedPreferences};
    await fileSystem.savePreferences(SharedStore.preferences);
}

export const init: ClientInit = async () => {
    const fsReady = initializeFileSystem();
    const serverReady = connectToLocalServer().then(async () => await loadAccounts());
    Promise.all([fsReady, serverReady]).then(() => {
        document.dispatchEvent(new CustomEvent("app-loaded"));
    });
};
