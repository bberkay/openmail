import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { Email } from '../types';

export const currentEmail: Writable<Email> = writable({} as Email);
export const emails: Writable<Email[]> = writable([]);
export const currentFolder: Writable<string> = writable('Inbox');
export const totalEmailCount: Writable<number> = writable(0);