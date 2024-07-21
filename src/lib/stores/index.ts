import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Email } from '../types';

export const emails: Writable<Email[]> = writable([]);
export const folders: Writable<string[]> = writable([]);
export const currentEmail: Writable<Email> = writable({} as Email);
export const currentFolder: Writable<string> = writable('Inbox');
export const currentOffset: Writable<number> = writable(0);
export const totalEmailCount: Writable<number> = writable(0);