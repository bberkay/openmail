import { Theme, Language, MailboxLength, type NotificationStatus, type Preferences } from ".";
import { PUBLIC_SERVER_URL } from "$env/static/public";

export const DEFAULT_PREFERENCES: Preferences = {
    serverURL: PUBLIC_SERVER_URL,
    theme: Theme.System,
    language: Language.EN_US,
    mailboxLength: MailboxLength.Fast,
    isAutostartEnabled: false,
    isSendDelayEnabled: true,
    notificationStatus: true
};
