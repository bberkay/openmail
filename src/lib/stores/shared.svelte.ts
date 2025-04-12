import {
    type Email,
    type Account,
    type Mailbox,
    type OpenMailTaskResults,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    accounts = "accounts",
    currentAccount = "currentAccount",
    folders = "folders",
    hierarchyDelimiters = "hierarchyDelimiters",
    recentEmails = "recentEmails",
    mailboxes = "mailboxes",
    failedAccounts = "failedAccounts",
    failedMailboxes = "failedMailboxes",
    failedFolders = "failedFolders"
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.folders]: OpenMailTaskResults<{
        standard: string[],
        custom: string[]
    }>;
    [SharedStoreKeys.hierarchyDelimiters]: OpenMailTaskResults<string>;
    [SharedStoreKeys.recentEmails]: OpenMailTaskResults<Email[]>;
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.failedFolders]: Account[]; // Accounts of failed folders
    [SharedStoreKeys.failedMailboxes]: Account[]; // Accounts of failed mailboxes
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.folders]: {},
    [SharedStoreKeys.hierarchyDelimiters]: {},
    [SharedStoreKeys.recentEmails]: {},
    [SharedStoreKeys.mailboxes]: {},
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.failedFolders]: [],
    [SharedStoreKeys.failedMailboxes]: [],
});
