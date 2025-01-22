import {
    Folder,
    type Account,
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
    currentAccount = "currentAccount"
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.standardFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.customFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.currentFolder]: string;
    [SharedStoreKeys.currentAccount]: Account | null;
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] }  = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.mailboxes]: [],
    [SharedStoreKeys.standardFolders]: [],
    [SharedStoreKeys.customFolders]: [],
    [SharedStoreKeys.currentFolder]: Folder.Inbox,
    [SharedStoreKeys.currentAccount]: null,
});
