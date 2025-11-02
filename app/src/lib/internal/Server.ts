import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService } from "$lib/services/ApiService";
import { AccountController } from "$lib/account";

const SERVER_CONNECTION_TRY_SLEEP_MS = 500;
const MAX_RETRY_COUNT = 5;

async function loadAccounts(): Promise<void> {
    if (!SharedStore.server)
        throw new Error("Server must be initialized before loading accounts.");

    await AccountController.init();
}

export async function connectToServer(targetServerURL: string): Promise<boolean> {
    console.log("wa a: ", targetServerURL);
    if (targetServerURL.length < 3)
        return false;
    console.log("1231 a: ", targetServerURL);
    for (let i = 0; i < MAX_RETRY_COUNT; i++) {
        await new Promise(resolve => setTimeout(resolve, SERVER_CONNECTION_TRY_SLEEP_MS));
        try {
            const response = await ApiService.hello(targetServerURL);
            if (response.success) {
                SharedStore.server = targetServerURL;
                await loadAccounts();
                return true;
            }
        } catch {}
    }

    return false;
}
