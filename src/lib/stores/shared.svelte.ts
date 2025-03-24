import {
    type Email,
    type Account,
    type Mailbox,
    type OpenMailTaskResults,
    Folder
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
    currentFolder = "currentFolder"
}

interface ISharedStore {
    [SharedStoreKeys.server]: string;
    [SharedStoreKeys.accounts]: Account[];
    [SharedStoreKeys.failedAccounts]: Account[];
    [SharedStoreKeys.recentEmails]: OpenMailTaskResults<string[]>; // uid list
    [SharedStoreKeys.mailboxes]: OpenMailTaskResults<Mailbox>;
    [SharedStoreKeys.standardFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.customFolders]: OpenMailTaskResults<string[]>;
    [SharedStoreKeys.currentAccount]: "home" | Account;
    [SharedStoreKeys.currentMailbox]: Mailbox;
    [SharedStoreKeys.currentFolder]: string;
}

export let SharedStore: { [K in SharedStoreKeys]: ISharedStore[K] }  = $state({
    [SharedStoreKeys.server]: "",
    [SharedStoreKeys.accounts]: [],
    [SharedStoreKeys.failedAccounts]: [],
    [SharedStoreKeys.recentEmails]: [],
    [SharedStoreKeys.mailboxes]: [],
    [SharedStoreKeys.standardFolders]: [],
    [SharedStoreKeys.customFolders]: [],
    [SharedStoreKeys.currentAccount]: "home",
    [SharedStoreKeys.currentMailbox]: { emails: [], folder: "", total: 0 },
    [SharedStoreKeys.currentFolder]: Folder.Inbox,
});

SharedStore.currentFolder = $derived(
    SharedStore.currentAccount === "home"
        ? Folder.Inbox
        : SharedStore.currentFolder
);

SharedStore.currentMailbox = $derived.by(() => {
    if (SharedStore.currentAccount === "home") {
        return {
            folder: Folder.Inbox,
            emails: SharedStore.mailboxes.map(task => task.result.emails).flat(),
            total: SharedStore.mailboxes.reduce((acc, task) => acc + task.result.total, 0)
        }
    } else {
        return SharedStore.mailboxes.find(
            (task) =>
                task.email_address ===
                    (SharedStore.currentAccount as Account).email_address &&
                task.result.folder === SharedStore.currentFolder,
        )!.result
    }
});
