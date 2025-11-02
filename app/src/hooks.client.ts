import type { ClientInit } from "@sveltejs/kit";
import { SharedStore } from "$lib/stores/shared.svelte";
import { FileSystem } from "$lib/internal/FileSystem";
import { PreferenceManager, PreferenceStore } from "$lib/preferences";
import { connectToServer } from "$lib/internal/Server";

async function initializeFileSystem(): Promise<void> {
    const fileSystem = await FileSystem.getInstance();
    const savedPreferences = await fileSystem.readPreferences();
    PreferenceManager.init(savedPreferences);
}

export const init: ClientInit = async () => {
    await initializeFileSystem();
    await connectToServer(PreferenceStore.serverURL);
    SharedStore.isAppLoaded = true;
};
