import { Language, Theme, type Preferences } from "$lib/types";

export const DEFAULT_LANGUAGE = "en"; // TODO: Remove this later.
export const MAILBOX_LENGTH = 10; // TODO: Remove this later.
export const DEFAULT_PREFERENCES: Preferences = {
    theme: Theme.System,
    language: Language.EN_US,
    mailboxLength: 10
};

export const MIN_MAILBOX_LENGTH = 10;
export const MAX_MAILBOX_LENGTH = 100;

export const GENERAL_FADE_DURATION_MS = 100;
export const REALTIME_SEARCH_DELAY_MS = 300;
export const PAGINATE_MAILBOX_CHECK_DELAY_MS = 100;
export const WAIT_FOR_EMAILS_TIMEOUT_MS = 50000;
export const SEND_RECALL_DELAY_MS = 5000;
export const AUTO_SAVE_DRAFT_INTERVAL_MS = 5000;
