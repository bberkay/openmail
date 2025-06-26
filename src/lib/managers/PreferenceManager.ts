import { DEFAULT_PREFERENCES } from "$lib/constants";
import { FileSystem } from "$lib/services/FileSystem";
import {
    Language,
    MailboxLength,
    Theme,
    type NotificationStatus,
    type Preferences,
} from "$lib/types";
import { enable, disable } from "@tauri-apps/plugin-autostart";
import {
    convertToLanguageEnum,
    convertToRFC5646Format,
    convertToThemeEnum,
    getEnumValueByKey,
    simpleDeepCopy,
} from "$lib/utils";
import { locale } from "@tauri-apps/plugin-os";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { NotificationManager } from "./NotificationManager";
import { SharedStore } from "$lib/stores/shared.svelte";
import { PreferencesStore } from "$lib/stores/PreferencesStore";
import { MailboxController } from "$lib/controllers/MailboxController";
import { _getPreferences, _initPreferences, _isPreferencesInitialized, _updatePreferences } from "../internal/preferences.internal";

let saveOperationQueue: ((() => Promise<void>) | (() => void))[] = [];

function IsPreferencesLoaded(
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
) {
    const { value, get } = descriptor;
    if (!(value || get)) return;

    const method = value ? "value" : "get";
    descriptor[method] = function (...args: any[]) {
        if (!_isPreferencesInitialized())
            throw new Error(
                "Preferences are not loaded. Please use `init()` before calling any other `PreferenceManager` method.",
            );
        return value.apply(null, args);
    };
    return descriptor;
}

export class PreferenceManager {
    public static init(preferences: Preferences) {
        _initPreferences(preferences)
    }

    @IsPreferencesLoaded
    public static async changeLanguage(targetLanguage: Language) {
        targetLanguage = getEnumValueByKey(
            Language,
            targetLanguage as keyof typeof Language
        );

        let foundLocale: Language = Language.System;
        if (targetLanguage === Language.System) {
            const preferredLocale = await locale();
            foundLocale = preferredLocale
                ? convertToLanguageEnum(preferredLocale) || Language.EN_US
                : Language.EN_US;
        } else {
            foundLocale = targetLanguage;
        }

        const legalLocale = convertToRFC5646Format(foundLocale);
        document.documentElement.setAttribute("lang", legalLocale);

        const onSave = () => {
            _updatePreferences({ language: targetLanguage })
            localStorage.setItem("lang", legalLocale);
        }
        saveOperationQueue.push(onSave);
    }

    public static async resetLanguage() {
        await PreferenceManager.changeLanguage(DEFAULT_PREFERENCES.language);
    }

    @IsPreferencesLoaded
    public static async changeTheme(targetTheme: Theme) {
        targetTheme = getEnumValueByKey(
            Theme,
            targetTheme as keyof typeof Theme,
        );

        let foundTheme = "";
        if (targetTheme === Theme.System) {
            const preferredTheme = await getCurrentWindow().theme();
            foundTheme = preferredTheme
                ? convertToThemeEnum(preferredTheme) || Theme.Dark
                : Theme.Dark;
        } else {
            foundTheme = targetTheme;
        }

        const legalTheme = foundTheme.toLowerCase();
        document.documentElement.setAttribute("data-color-scheme", legalTheme);
        const onSave = () => {
            _updatePreferences({ theme: targetTheme });
            localStorage.setItem("data-color-scheme", legalTheme);
        }
        saveOperationQueue.push(onSave);
    }

    public static async resetTheme() {
        await PreferenceManager.changeTheme(DEFAULT_PREFERENCES.theme);
    }

    @IsPreferencesLoaded
    public static async changeAutostart(newAutostartStatus: boolean) {
        const onSave = async () => {
            _updatePreferences({ isAutostartEnabled: newAutostartStatus });
            if (newAutostartStatus) {
                await enable();
            } else {
                await disable();
            }
        };
        saveOperationQueue.push(onSave);
    }

    public static async resetAutostart() {
        await PreferenceManager.changeAutostart(
            DEFAULT_PREFERENCES.isAutostartEnabled,
        );
    }

    @IsPreferencesLoaded
    public static changeSendDelay(newSendDelayStatus: boolean) {
        const onSave = async () => {
            _updatePreferences({ isSendDelayEnabled: newSendDelayStatus });
        };
        saveOperationQueue.push(onSave);
    }

    public static resetSendDelay() {
        PreferenceManager.changeSendDelay(
            DEFAULT_PREFERENCES.isSendDelayEnabled,
        );
    }

    @IsPreferencesLoaded
    public static async changeMailboxLength(newMailboxLength: MailboxLength) {
        const onSave = async () => {
            await MailboxController.initMailboxes();
            _updatePreferences({ mailboxLength: newMailboxLength });
        };
        saveOperationQueue.push(onSave);
    }

    public static async resetMailboxLength() {
        await PreferenceManager.changeMailboxLength(
            DEFAULT_PREFERENCES.mailboxLength,
        );
    }

    @IsPreferencesLoaded
    public static checkNotificationStatus(email_address: string): boolean {
        const notificationStatus = PreferencesStore.notificationStatus;
        if (typeof notificationStatus === "boolean")
            return notificationStatus;

        return (
            Object.hasOwn(
                notificationStatus,
                email_address,
            ) && NotificationManager.hasChannel(email_address)
        );
    }

    @IsPreferencesLoaded
    public static async changeNotificationStatus(
        newNotificationStatus: NotificationStatus,
        deleteRecord: boolean = false,
    ) {
        const onSave = () => {
            if (typeof newNotificationStatus === "boolean") {
                if (newNotificationStatus) {
                    SharedStore.accounts.forEach((acc) =>
                        NotificationManager.create(acc),
                    );
                } else {
                    NotificationManager.terminateAll();
                }
                _updatePreferences({ notificationStatus: newNotificationStatus });
                return;
            }

            let currentNotificationStatus = simpleDeepCopy(PreferencesStore.notificationStatus);

            if (typeof currentNotificationStatus === "boolean") {
                const originalStatus = currentNotificationStatus;
                currentNotificationStatus = {};
                for (const acc of SharedStore.accounts) {
                    currentNotificationStatus[acc.email_address] = originalStatus;
                }
            }

            Object.entries(newNotificationStatus).forEach(
                ([email_address, status]) => {
                    const acc = SharedStore.accounts.find(
                        (acc) => acc.email_address === email_address,
                    )!;
                    if (status) {
                        NotificationManager.create(acc);
                    } else {
                        NotificationManager.terminate(acc);
                    }
                },
            );

            currentNotificationStatus = {
                ...currentNotificationStatus,
                ...newNotificationStatus,
            };

            if (deleteRecord) {
                for (const email_address in newNotificationStatus) {
                    if (newNotificationStatus[email_address])
                        continue;
                    if (Object.hasOwn(currentNotificationStatus, email_address)) {
                        delete currentNotificationStatus[email_address]
                    }
                }
            }

            _updatePreferences({ notificationStatus: currentNotificationStatus });
        }
        saveOperationQueue.push(onSave);
    }

    public static async resetNotificationStatus() {
        await PreferenceManager.changeNotificationStatus(
            DEFAULT_PREFERENCES.notificationStatus,
        );
    }

    @IsPreferencesLoaded
    public static async resetToDefault() {
        PreferenceManager.resetSendDelay();
        await PreferenceManager.resetTheme();
        await PreferenceManager.resetLanguage();
        await PreferenceManager.resetAutostart();
        await PreferenceManager.resetMailboxLength();
        await PreferenceManager.resetNotificationStatus();
    }

    @IsPreferencesLoaded
    public static async savePreferences() {
        await Promise.all(saveOperationQueue.map((op) => Promise.resolve(op())));
        const fs = await FileSystem.getInstance();
        await fs.savePreferences(_getPreferences());
        saveOperationQueue = [];
    }
}
