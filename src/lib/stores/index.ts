import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import type { User, Email } from '../types';

export const serverUrl: Writable<string> = writable('http://127.0.0.1:8000');
export const user: Writable<User> = writable({ fullname: '', email: '' });
export const emails: Writable<Email[]> = writable([]);
export const folders: Writable<string[]> = writable([]);
export const currentEmail: Writable<Email> = writable({} as Email);
export const currentFolder: Writable<string> = writable('Inbox');
export const currentOffset: Writable<number> = writable(0);
export const totalEmailCount: Writable<number> = writable(0);
