import type { Preferences } from "$lib/types";

let _currentPreferences: Preferences | null = null;

function assertPreferencesInitialized() {
    if (!_isPreferencesInitialized()) {
        throw new Error("Preferences are not loaded. Please use `PreferenceManager.init()`.");
    }
}

export function _initPreferences(preferences: Preferences) {
    if (_currentPreferences !== null) {
        throw new Error("Preferences already loaded.");
    }
    _currentPreferences = preferences;
}

export function _getPreferences(): Preferences {
    assertPreferencesInitialized();
    return { ..._currentPreferences! };
}

export function _updatePreferences(preferences: Partial<Preferences>) {
    assertPreferencesInitialized();
    _currentPreferences = { ..._currentPreferences!, ...preferences };
}

export function _isPreferencesInitialized() {
    return !!_currentPreferences;
}
