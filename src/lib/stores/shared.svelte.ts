import { DEFAULT_PREFERENCES } from "../constants";
import {
    type Email,
    type Account,
    type Mailbox,
    type OpenmailTaskResults,
    type Preferences,
} from "../types";

export enum SharedStoreKeys {
    server = "server",
    isAppLoaded = "isAppLoaded",
    preferences = "preferences",
    accounts = "accounts",
    currentAccount = "currentAccount",
    folders = "folders",
    hierarchyDelimiters = "hierarchyDelimiters",
    recentEmails = "recentEmails",
    mailboxes = "mailboxes",
    failedAccounts = "failedAccounts",
    accountsWithFailedFolders = "accountsWithFailedFolders",
    accountsWithFailedMailboxes = "accountsWithFailedMailboxes",
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.isAppLoaded]: boolean;
    [SharedStoreKeys.preferences]: Preferences;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.folders]: OpenmailTaskResults<{
        standard: string[],
        custom: string[]
    }>;
    [SharedStoreKeys.hierarchyDelimiters]: OpenmailTaskResults<string>;
    [SharedStoreKeys.recentEmails]: OpenmailTaskResults<Email[]>;
    [SharedStoreKeys.mailboxes]: OpenmailTaskResults<Mailbox>;
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.accountsWithFailedFolders]: Account[];
    [SharedStoreKeys.accountsWithFailedMailboxes]: Account[];
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] } = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.isAppLoaded]: false,
    [SharedStoreKeys.preferences]: DEFAULT_PREFERENCES,
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.folders]: {},
    [SharedStoreKeys.hierarchyDelimiters]: {},
    [SharedStoreKeys.recentEmails]: {},
    [SharedStoreKeys.mailboxes]: {},
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.accountsWithFailedFolders]: [],
    [SharedStoreKeys.accountsWithFailedMailboxes]: [],
});
