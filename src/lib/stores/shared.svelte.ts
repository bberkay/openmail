import type { GetRoutes, GetQueryResponse } from "$lib/services/ApiService";
import {
    Folder,
    type Account,
    type EmailWithContent,
    type Mailbox,
    type OpenMailTaskResults,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    accounts = "accounts",
    failedAccounts = "failedAccounts",
    mailboxes = "mailboxes",
    standardFolders = "standardFolders",
    customFolders = "customFolders",
    currentFolder = "currentFolder",
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.standardFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.customFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.currentFolder]: string;
}

export const DefaultSharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = {
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.mailboxes]: [],
    [SharedStoreKeys.standardFolders]: [],
    [SharedStoreKeys.customFolders]: [],
    [SharedStoreKeys.currentFolder]: Folder.Inbox,
};

let nonSharedState = $state(DefaultSharedStore);

export class SharedStore {
    /**
     * Getters
     */

    public static get server(): ISharedStore[SharedStoreKeys.server] {
        return nonSharedState[SharedStoreKeys.server];
    }

    public static get accounts(): ISharedStore[SharedStoreKeys.accounts] {
        return nonSharedState[SharedStoreKeys.accounts];
    }

    public static get failedAccounts(): ISharedStore[SharedStoreKeys.failedAccounts] {
        return nonSharedState[SharedStoreKeys.failedAccounts];
    }

    public static get mailboxes(): ISharedStore[SharedStoreKeys.mailboxes] {
        return nonSharedState[SharedStoreKeys.mailboxes];
    }

    public static get standardFolders(): ISharedStore[SharedStoreKeys.standardFolders] {
        return nonSharedState[SharedStoreKeys.standardFolders];
    }

    public static get customFolders(): ISharedStore[SharedStoreKeys.customFolders] {
        return nonSharedState[SharedStoreKeys.customFolders];
    }

    public static get currentFolder(): ISharedStore[SharedStoreKeys.currentFolder] {
        return nonSharedState[SharedStoreKeys.currentFolder];
    }

    /**
     * Setters
     */

    public static set server(server: string) {
        nonSharedState[SharedStoreKeys.server] = server;
    }

    public static set accounts(
        data: GetQueryResponse[GetRoutes.GET_ACCOUNTS] | Account[],
    ) {
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

    public static set mailboxes(
        data: GetQueryResponse[GetRoutes.GET_MAILBOXES],
    ) {
        nonSharedState[SharedStoreKeys.mailboxes] = data;
    }

    public static set standardFolders(
        data: GetQueryResponse[GetRoutes.GET_FOLDERS],
    ) {
        nonSharedState[SharedStoreKeys.standardFolders] = data;
    }

    public static set customFolders(
        data: GetQueryResponse[GetRoutes.GET_FOLDERS],
    ) {
        nonSharedState[SharedStoreKeys.customFolders] = data;
    }

    public static set currentFolder(folder: string) {
        nonSharedState[SharedStoreKeys.currentFolder] = folder;
    }

    /* Custom Methods */

    public static keys(): SharedStoreKeys[] {
        return Object.values(SharedStoreKeys);
    }

    public static toString(): string {
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
