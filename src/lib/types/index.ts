export interface Response {
  success: boolean;
  message: string;
  data?: any;
}

export interface Account {
  fullname: string;
  email: string;
}

export interface Email {
  uid: string;
  from: string;
  to: string;
  subject: string;
  body_short?: string; // This or body is optional
  body?: string; // This or body_short is optional
  date: string;
  attachments?: Attachment[];
  flags: string[];
}

export interface SearchCriteria {
  senders: string[] | null;
  receivers: string[] | null;
  subject: string | null;
  since: string | null;
  before: string | null;
  flags: string[] | null;
  include: string | null;
  exclude: string | null;
  has_attachments: boolean;
}

export interface Attachment {
  cid: string;
  name: string;
  data: string;
  size: string;
  type: string;
}

export type Inboxes = { email: string, folder: string, emails:Email[], total: number }[];
export type Folders = { email: string, folders:string[] }[];

export interface SharedStore {
    server: string;
    accounts: Account[];
    inboxes: Inboxes;
    folders: Folders;
    selectedAccounts: Account[];
    selectedFolder: string;
    selectedEmail: Email | null;
    currentOffset: number;
}
