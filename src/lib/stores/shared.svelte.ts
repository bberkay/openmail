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

$effect(() => {
    if (SharedStore.currentAccount) {
        SharedStore.currentFolder = Folder.Inbox;
        if (SharedStore.currentAccount === "home") {
            SharedStore.currentMailbox = {
                folder: Folder.Inbox,
                emails: SharedStore.mailboxes
                    .map((task) => task.result.emails)
                    .flat()
                    .sort(
                        (a, b) =>
                            new Date(b.date).getTime() - new Date(a.date).getTime(),
                    ),
                total: SharedStore.mailboxes.reduce(
                    (acc, task) => acc + task.result.total,
                    0,
                ),
            }
        } else {
            SharedStore.currentMailbox = SharedStore.mailboxes.find(
                (task) =>
                    task.email_address ===
                        (SharedStore.currentAccount as Account).email_address &&
                    task.result.folder === SharedStore.currentFolder,
            )!.result;
        }
    }
})

/* TODO: Check out this later */
SharedStore.recentEmails = $derived.by(() => {
    return SharedStore.recentEmails.concat(
        SharedStore.accounts
            .map((account) => {
                return {
                    email_address: account.email_address,
                    result:
                        SharedStore.recentEmails.find(
                            (recentAcc) =>
                                recentAcc.email_address ===
                                account.email_address,
                        )?.result || [],
                };
            })
            .flat(),
    );
});
