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

export type NotificationStatus = true | false | { [email_address: string]: boolean };

export interface Preferences {
    theme: Theme;
    language: Language;
    mailboxLength: MailboxLength;
    isAutostartEnabled: boolean;
    isSendDelayEnabled: boolean;
    notificationStatus: NotificationStatus;
}
