import { Theme, Language, MailboxLength, type NotificationStatus, type Preferences } from ".";

export const DEFAULT_PREFERENCES: Preferences = {
    serverURL: "",
    theme: Theme.System,
    language: Language.EN_US,
    mailboxLength: MailboxLength.Fast,
    isAutostartEnabled: false,
    isSendDelayEnabled: true,
    notificationStatus: true
};
