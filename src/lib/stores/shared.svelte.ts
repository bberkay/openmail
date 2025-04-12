import {
    type Email,
    type Account,
    type Mailbox,
    type OpenMailTaskResults,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    accounts = "accounts",
    failedAccounts = "failedAccounts",
    hierarchyDelimiters = "hierarchyDelimiters",
    currentAccount = "currentAccount",
    recentEmails = "recentEmails",
    mailboxes = "mailboxes",
    failedMailboxes = "failedMailboxes",
    folders = "folders",
    failedFolders = "failedFolders"
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.hierarchyDelimiters]: OpenMailTaskResults<string>;
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.recentEmails]: OpenMailTaskResults<Email[]>;
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.failedMailboxes]: Account[]; // Accounts of failed mailboxes
    [SharedStoreKeys.folders]: OpenMailTaskResults<{
        standard: string[],
        custom: string[]
    }>;
    [SharedStoreKeys.failedFolders]: Account[]; // Accounts of failed folders
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.hierarchyDelimiters]: {},
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.recentEmails]: {},
    [SharedStoreKeys.mailboxes]: {},
    [SharedStoreKeys.failedMailboxes]: [],
    [SharedStoreKeys.folders]: {},
    [SharedStoreKeys.failedFolders]: [],
});
