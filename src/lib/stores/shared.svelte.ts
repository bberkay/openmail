import {
    type Email,
    type Account,
    type Mailbox,
    type OpenmailTaskResults,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    isAppLoaded = "isAppLoaded",
    accounts = "accounts",
    currentAccount = "currentAccount",
    folders = "folders",
    hierarchyDelimiters = "hierarchyDelimiters",
    recentEmailsChannel = "recentEmailsChannel",
    mailboxes = "mailboxes",
    failedAccounts = "failedAccounts",
    accountsWithFailedFolders = "accountsWithFailedFolders",
    accountsWithFailedMailboxes = "accountsWithFailedMailboxes",
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.isAppLoaded]: boolean;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.folders]: OpenmailTaskResults<{
        standard: string[],
        custom: string[]
    }>;
    [SharedStoreKeys.hierarchyDelimiters]: OpenmailTaskResults<string>;
    [SharedStoreKeys.recentEmailsChannel]: OpenmailTaskResults<Email[]>; // TODO: Check out this later...
    [SharedStoreKeys.mailboxes]: OpenmailTaskResults<Mailbox>;
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.accountsWithFailedFolders]: Account[];
    [SharedStoreKeys.accountsWithFailedMailboxes]: Account[];
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.isAppLoaded]: false,
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.folders]: {},
    [SharedStoreKeys.hierarchyDelimiters]: {},
    [SharedStoreKeys.recentEmailsChannel]: {},
    [SharedStoreKeys.mailboxes]: {},
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.accountsWithFailedFolders]: [],
    [SharedStoreKeys.accountsWithFailedMailboxes]: [],
});
