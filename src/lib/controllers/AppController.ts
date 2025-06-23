import { DEFAULT_PREFERENCES } from "$lib/constants";
import { SharedStore } from "$lib/stores/shared.svelte";
import { FileSystem } from "$lib/services/FileSystem";
import { Language, MailboxLength, Theme } from "$lib/types";
import { MailboxController } from "$lib/controllers/MailboxController";
import { enable, disable } from "@tauri-apps/plugin-autostart";
import { convertToLanguageEnum, convertToRFC5646Format, convertToThemeEnum, getEnumValueByKey } from "$lib/utils";
import { locale } from "@tauri-apps/plugin-os";
import { getCurrentWindow } from "@tauri-apps/api/window";

export class AppController {
    public static async changeLanguage(newLanguage: Language) {
        SharedStore.preferences.language = getEnumValueByKey(
            Language,
            newLanguage as keyof typeof Language,
        );

        let foundLocale: Language = Language.System;
        if (SharedStore.preferences.language === Language.System) {
            const preferredLocale = await locale();
            foundLocale = preferredLocale
                ? convertToLanguageEnum(preferredLocale) || Language.EN_US
                : Language.EN_US;
        } else {
            foundLocale = SharedStore.preferences.language;
        }

        const legalLocale = convertToRFC5646Format(foundLocale);
        document.documentElement.setAttribute("lang", legalLocale);
    }

    public static async resetLanguage() {
        await AppController.changeLanguage(DEFAULT_PREFERENCES.language);
    }

    public static async changeTheme(newTheme: Theme) {
        SharedStore.preferences.theme = getEnumValueByKey(
            Theme,
            newTheme as keyof typeof Theme,
        );

        let foundTheme = "";
        if(SharedStore.preferences.theme === Theme.System) {
            const preferredTheme = await getCurrentWindow().theme();
            foundTheme = (preferredTheme
                ? convertToThemeEnum(preferredTheme) || Theme.Dark
                : Theme.Dark).toLowerCase();
        } else {
            foundTheme = SharedStore.preferences.theme.toLowerCase();
        }

        document.documentElement.setAttribute("data-color-scheme", foundTheme);
    }

    public static async resetTheme() {
        await AppController.changeTheme(DEFAULT_PREFERENCES.theme);
    }

    public static async changeAutostart(newAutostartStatus: boolean) {
        SharedStore.preferences.isAutostartEnabled = newAutostartStatus;
        if (newAutostartStatus) {
            await enable();
        } else {
            disable();
        }
    }

    public static async resetAutostart() {
        await AppController.changeAutostart(DEFAULT_PREFERENCES.isAutostartEnabled);
    }

    public static changeSendDelay(newSendDelayStatus: boolean) {
        SharedStore.preferences.isSendDelayEnabled = newSendDelayStatus;
    }

    public static resetSendDelay() {
        AppController.changeSendDelay(DEFAULT_PREFERENCES.isSendDelayEnabled);
    }

    public static async changeMailboxLength(newMailboxLength: MailboxLength) {
        SharedStore.preferences.mailboxLength = newMailboxLength;
        await MailboxController.init();
    }

    public static async resetMailboxLength() {
        await AppController.changeMailboxLength(DEFAULT_PREFERENCES.mailboxLength);
    }

    public static async resetToDefault() {
        SharedStore.preferences = DEFAULT_PREFERENCES;
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences(SharedStore.preferences);
    }
}
