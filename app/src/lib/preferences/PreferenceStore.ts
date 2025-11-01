import { _getPreferences } from "./preferences.internal";
import { type Preferences } from "./types";

export class PreferenceStore {
    public static get serverURL(): Preferences["serverURL"] {
        return _getPreferences().serverURL;
    }

    public static get theme(): Preferences["theme"] {
        return _getPreferences().theme;
    }

    public static get language(): Preferences["language"] {
        return _getPreferences().language;
    }

    public static get mailboxLength(): number {
        return Number(_getPreferences().mailboxLength);
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
