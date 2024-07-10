export interface OpenMailData {
    success: boolean;
    message: string;
    data?: object;
}

export type OpenMailDataString = string;

export interface Email {
    id: string,
    from: string,
    to: string,
    subject: string,
    body_short: string,
    date: string,
    flags: string
}
