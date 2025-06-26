import { _getPreferences } from "../internal/preferences.internal";
import { type Preferences } from "$lib/types";

export class PreferencesStore {
    public static get theme(): Preferences["theme"] {
        return _getPreferences().theme;
    }

    public static get language(): Preferences["language"] {
        return _getPreferences().language;
    }

    public static get mailboxLength(): Preferences["mailboxLength"] {
        return _getPreferences().mailboxLength;
    }

    public static get isAutostartEnabled(): Preferences["isAutostartEnabled"] {
        return _getPreferences().isAutostartEnabled;
    }

    public static get isSendDelayEnabled(): Preferences["isSendDelayEnabled"] {
        return _getPreferences().isSendDelayEnabled;
    }

    public static get notificationStatus(): Preferences["notificationStatus"] {
        return _getPreferences().notificationStatus;
    }
}
