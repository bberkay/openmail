import { SharedStore } from "$lib/stores/shared.svelte";
import { error } from "@sveltejs/kit";
import type { PageLoad } from './$types';
import { AccountController } from "$lib/controllers/AccountController";

/**
 * Load the accounts from the server
 * and set them in the shared store
 */
async function loadAccounts() {
    if(!SharedStore.server)
        return;

    const response = await AccountController.init();
    if (!response.success) {
        error(500, response.message);
    }
}

export const load: PageLoad = async ({}) => {
    await loadAccounts();
};
