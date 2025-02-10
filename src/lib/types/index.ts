export enum TauriCommand {
    GET_SERVER_URL = "get_server_url",
}

export interface Account {
    email_address: string;
    fullname?: string;
}

export interface Email {
    message_id: string;
    uid: string;
    sender: string | [string, string];
    receiver: string;
    date: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
    flags?: string[];
    attachments?: Attachment[];
    in_reply_to?: string;
    references?: string;
    list_unsubscribe?: string;
}

export interface SearchCriteria {
    senders?: string[];
    receivers?: string[];
    cc?: string[];
    bcc?: string[];
    subject?: string;
    since?: string;
    before?: string;
    smaller_than?: number;
    larger_than?: number;
    include?: string;
    exclude?: string;
    included_flags?: string[];
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
    sender: string | [string, string];
    receiver: string;
    //date: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
    attachments?: Attachment[];
    in_reply_to?: string;
    references?: string;
    metadata?: Record<string, string>;
    mail_options?: string[];
    rcpt_options?: string[];
}

export interface OpenMailTaskResult<T> {
    email_address: string;
    result: T;
}

export type OpenMailTaskResults<T> = OpenMailTaskResult<T>[];

export interface Mailbox {
    folder: string;
    emails: Email[];
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
    Undeleted = "\\Undeleted"
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
