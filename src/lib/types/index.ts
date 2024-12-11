export interface Account {
    fullname: string;
    email_address: string;
}

export interface EmailSummary {
    uid: string;
    sender: string;
    receiver: string;
    date: string;
    subject: string;
    body_short: string;
    flags?: string[];
    attachments?: Attachment[];
}

export interface EmailWithContent {
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
    message_id?: string;
    metadata?: Record<string, string>;
}

export interface SearchCriteria {
    senders: string[] | null;
    receivers: string[] | null;
    cc: string[] | null;
    bcc: string[] | null;
    subject: string | null;
    since: string | null;
    before: string | null;
    included_flags: string[] | null;
    excluded_flags: string[] | null;
    smaller_than: number | null;
    larger_than: number | null;
    include: string | null;
    exclude: string | null;
    has_attachments: boolean;
}

export interface Attachment {
    name: string;
    data: string;
    size: string;
    type: string;
    cid: string | null;
}

export interface SharedStore {
    server: string;
    accounts: Account[];
    mailboxes: any;
    folders: any;
    selectedAccounts: Account[];
    selectedFolder: string;
    selectedEmail: EmailWithContent | null;
    currentOffset: number;
}

export enum TauriCommand {
    GET_SERVER_URL = "get_server_url",
}
