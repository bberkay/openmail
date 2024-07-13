export interface OpenMailData {
    success: boolean;
    message: string;
    data?: any;
}

export type OpenMailDataString = string;

export interface Attachment {
    cid: string;
    name: string;
    data: string;
    size: string;
    type: string;
}

export interface Email {
    id: string,
    from: string,
    to: string,
    subject: string,
    body_short?: string, // This or body is optional
    body?: string, // This or body_short is optional
    date: string,
    attachments?: Attachment[], 
    flags: string[]
}
