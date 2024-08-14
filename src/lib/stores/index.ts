import { writable } from "svelte/store";
import type { Writable } from "svelte/store";
import type { Email, Accounts, Emails, Folders } from "../types";

export const serverUrl: Writable<string> = writable("");

export const accounts: Writable<Accounts> = writable([]);
export const emails: Writable<Emails> = writable([]);
export const folders: Writable<Folders> = writable([]);

export const currentAccounts: Writable<Accounts> = writable([]);
export const currentFolder: Writable<string> = writable("Inbox");
export const currentEmail: Writable<Email | null> = writable(null);
export const currentOffset: Writable<number> = writable(0);
