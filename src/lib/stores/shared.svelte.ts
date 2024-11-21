import type { SharedStore } from "../types";

export let sharedStore: SharedStore = $state({
    server: "",
    accounts: [],
    inboxes: [],
    folders: [],
    selectedAccounts: [],
    selectedFolder: "Inbox",
    selectedEmail: null,
    currentOffset: 0
});