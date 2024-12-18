import type { SharedStore } from "../types";

export let sharedStore: SharedStore = $state({
    server: "",
    accounts: [],
    failedAccounts: [],
    mailboxes: [],
    folders: [],
    selectedAccounts: [],
    selectedFolder: "Inbox",
    selectedEmail: null,
    currentOffset: 0
});
