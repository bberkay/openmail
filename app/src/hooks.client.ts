import type { ClientInit } from "@sveltejs/kit";
import { invoke } from "@tauri-apps/api/core";
import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService } from "$lib/services/ApiService";
import { FileSystem } from "$lib/internal/FileSystem";
import { AccountController } from "$lib/account";
import { PreferenceManager } from "$lib/preferences";
import { PUBLIC_SERVER_URL } from "$env/static/public";

const SERVER_CONNECTION_TRY_SLEEP_MS = 500;

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    const savedPreferences = await fileSystem.readPreferences();
    PreferenceManager.init(savedPreferences);
}

async function connectToLocalServer(): Promise<void> {
    while (true) {
        await new Promise(resolve => setTimeout(resolve, SERVER_CONNECTION_TRY_SLEEP_MS));
        try {
            const response = await ApiService.hello(PUBLIC_SERVER_URL);
            if (response.success) {
                SharedStore.server = PUBLIC_SERVER_URL;
                return;
            }
        } catch {}
    }
}

async function loadAccounts(): Promise<void> {
    if (!SharedStore.server)
        throw new Error("Server must be initialized before loading accounts.");

    await AccountController.init();
}

export const init: ClientInit = async () => {
    const fsReady = initializeFileSystem();
    const serverReady = connectToLocalServer().then(async () => await loadAccounts());
    Promise.all([fsReady, serverReady]).then(() => {
        SharedStore.isAppLoaded = true;
    });
};
