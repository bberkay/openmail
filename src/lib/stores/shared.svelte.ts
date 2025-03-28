import {
    type Email,
    type Account,
    type Mailbox,
    type OpenMailTaskResults,
    Folder,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    accounts = "accounts",
    failedAccounts = "failedAccounts",
    mailboxes = "mailboxes",
    recentEmails = "recentEmails",
    standardFolders = "standardFolders",
    customFolders = "customFolders",
    currentAccount = "currentAccount",
    currentMailbox = "currentMailbox",
    currentFolder = "currentFolder",
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.recentEmails]: OpenMailTaskResults<Email[]>;
    [SharedStoreKeys.standardFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>
    [SharedStoreKeys.customFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.currentFolder]: string;
    [SharedStoreKeys.currentMailbox]: Mailbox
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.recentEmails]: {},
    [SharedStoreKeys.standardFolders]: {},
    [SharedStoreKeys.mailboxes]: {},
    [SharedStoreKeys.customFolders]: {},
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.currentFolder]: Folder.Inbox,
    [SharedStoreKeys.currentMailbox]: { folder: "", emails: { prev: [], current: [], next: [] } , total: 0},
});
