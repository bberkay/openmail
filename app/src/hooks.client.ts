import type { ClientInit } from "@sveltejs/kit";
import { SharedStore } from "$lib/stores/shared.svelte";
import { FileSystem } from "$lib/internal/FileSystem";
import { PreferenceManager } from "$lib/preferences";
import { connectToServer } from "$lib/internal/Server";

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    const savedPreferences = await fileSystem.readPreferences();
    PreferenceManager.init(savedPreferences);
}

export const init: ClientInit = async () => {
    const fsReady = initializeFileSystem();
    const serverReady = connectToServer();
    Promise.all([fsReady, serverReady]).then(() => {
        SharedStore.isAppLoaded = true;
    });
};
