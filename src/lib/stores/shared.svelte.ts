import type { GetRoutes, GetQueryResponse } from "$lib/services/ApiService";
import type { Account, EmailWithContent, Mailbox, OpenMailTaskResults } from "../types";

export enum SharedStoreKeys {
    server="server",
    accounts="accounts",
    failedAccounts="failedAccounts",
    mailboxes="mailboxes",
    folders="folders",
    selectedAccounts="selectedAccounts",
    selectedFolder="selectedFolder",
    shownEmail="shownEmail",
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.folders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.selectedAccounts]: Account[];
    [SharedStoreKeys.selectedFolder]: string;
    [SharedStoreKeys.shownEmail]: EmailWithContent | null;
}

export const DefaultSharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = {
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.mailboxes]: [],
    [SharedStoreKeys.folders]: [],
    [SharedStoreKeys.selectedAccounts]: [],
    [SharedStoreKeys.selectedFolder]: "Inbox",
    [SharedStoreKeys.shownEmail]: null,
}

let nonSharedState = $state(DefaultSharedStore);

export class SharedStore {

    /**
     * Getters
     */

    public static get server(): string { return nonSharedState[SharedStoreKeys.server] }
    public static get accounts(): Account[] { return nonSharedState[SharedStoreKeys.accounts] }
    public static get failedAccounts(): Account[] { return nonSharedState[SharedStoreKeys.failedAccounts] }
    public static get mailboxes(): OpenMailTaskResults<Mailbox> { return nonSharedState[SharedStoreKeys.mailboxes] }
    public static get folders(): OpenMailTaskResults<string[]> { return nonSharedState[SharedStoreKeys.folders] }
    public static get selectedAccounts(): Account[] { return nonSharedState[SharedStoreKeys.selectedAccounts] }
    public static get selectedFolder(): string { return nonSharedState[SharedStoreKeys.selectedFolder] }
    public static get shownEmail(): EmailWithContent | null { return nonSharedState[SharedStoreKeys.shownEmail] }

    /**
     * Setters
     */

    public static set server(server: string) {
        nonSharedState[SharedStoreKeys.server] = server;
    }

    public static set accounts(data: GetQueryResponse[GetRoutes.GET_ACCOUNTS] | Account[]) {
        if (Array.isArray(data)) {
            nonSharedState[SharedStoreKeys.accounts] = data;
            return;
        }

        nonSharedState[SharedStoreKeys.accounts] = data.connected;
        nonSharedState[SharedStoreKeys.failedAccounts] = data.failed;
    }

    public static set failedAccounts(accounts: Account[]) {
        nonSharedState[SharedStoreKeys.failedAccounts] = accounts;
    }

    public static set mailboxes(data: GetQueryResponse[GetRoutes.GET_MAILBOXES]) {
        nonSharedState[SharedStoreKeys.mailboxes] = data;
    }

    public static set folders(data: GetQueryResponse[GetRoutes.GET_FOLDERS]) {
        nonSharedState[SharedStoreKeys.folders] = data;
    }

    public static set selectedAccounts(accounts: Account[]) {
        nonSharedState[SharedStoreKeys.selectedAccounts] = accounts;
    }

    public static set selectedFolder(folder: string) {
        nonSharedState[SharedStoreKeys.selectedFolder] = folder;
    }

    public static set shownEmail(email: EmailWithContent | null) {
        nonSharedState[SharedStoreKeys.shownEmail] = email;
    }

    /* Custom Methods */

    public static keys(): SharedStoreKeys[]
    {
        return Object.values(SharedStoreKeys);
    }

    public static toString(): string
    {
        return JSON.stringify(nonSharedState, null, 2);
    }

    public static reset(...keys: SharedStoreKeys[]) {
        if (keys.length === 0) {
            keys = SharedStore.keys();
        }

        for (const key of keys) {
            if (key != SharedStoreKeys.server) {
                // @ts-ignore
                SharedStore[key] = DefaultSharedStore[key];
            }
        }
    }
}
