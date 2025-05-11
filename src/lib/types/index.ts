export enum TauriCommand {
    GET_SERVER_URL = "get_server_url",
}

export type OpenmailTaskResults<T> = {
    [email_address: string]: T;
};

export interface Account {
    email_address: string;
    fullname?: string;
}

export interface Email {
    message_id: string;
    uid: string;
    sender: string; // Name Surname <namesurname@domain.com> or namesurname@domain.com
    receivers: string; // mail addresses separated by comma
    date: string;
    subject: string;
    body: string;
    cc?: string; // mail addresses separated by comma
    bcc?: string; // mail addresses separated by comma
    flags?: string[];
    attachments?: Attachment[];
    in_reply_to?: string;
    references?: string;
    list_unsubscribe?: string;
    list_unsubscribe_post?: string;
}

export interface SearchCriteria {
    message_id?: string[];
    senders?: string[];
    receivers?: string[];
    cc?: string[];
    subject?: string;
    since?: string;
    before?: string;
    smaller_than?: number;
    larger_than?: number;
    include?: string;
    exclude?: string;
    included_flags?: string[];
    excluded_flags?: string[];
    has_attachments?: boolean;
}

export interface Attachment {
    name: string;
    size: string;
    type: string;
    data: string;
    path?: string;
    cid?: string;
}

export interface Draft {
    sender: string; // Name Surname <namesurname@domain.com> or namesurname@domain.com
    receivers: string | string[];
    //date: string;
    subject: string;
    body: string;
    cc?: string | string[];
    bcc?: string | string[];
    attachments?: Attachment[];
    in_reply_to?: string;
    references?: string;
    metadata?: Record<string, string>;
    mail_options?: string[];
    rcpt_options?: string[];
}

export interface RawMailbox {
    folder: string;
    emails: Email[];
    total: number;
}

export interface Mailbox {
    folder: string;
    emails: { prev: Email[]; current: Email[]; next: Email[] };
    total: number;
}

export interface Flags {
    uid: string;
    flags: string[];
}

export enum Mark {
    Flagged = "\\Flagged",
    Seen = "\\Seen",
    Answered = "\\Answered",
    Draft = "\\Draft",
    Deleted = "\\Deleted",
    Unflagged = "\\Unflagged",
    Unseen = "\\Unseen",
    Unanswered = "\\Unanswered",
    Undraft = "\\Undraft",
    Undeleted = "\\Undeleted",
}

export enum Folder {
    Inbox = "Inbox",
    Flagged = "Flagged",
    Important = "Important",
    Sent = "Sent",
    Drafts = "Drafts",
    All = "All",
    Archive = "Archive",
    Junk = "Junk",
    Trash = "Trash",
}

export enum Size {
    Bytes = "Bytes",
    KB = "KB",
    MB = "MB",
}

/**
 * The enum keys are derived from RFC 5646 language tags
 * (e.g., "en-US", "en-GB"),but are formatted using
 * uppercase letters and underscores (e.g., EN_US).
 * Reference: https://datatracker.ietf.org/doc/html/rfc5646
 */
export enum Language {
    System = "System",
    EN_US = "English (US)",
}

export enum Theme {
    System = "System",
    Light = "Light",
    Dark = "Dark",
}

export enum MailboxLength {
    Fast = "10",
    Standard = "50",
    Compact = "100"
}

export interface Preferences {
    theme: Theme;
    language: Language;
    mailboxLength: MailboxLength;
    isAutostartEnabled: boolean;
}
