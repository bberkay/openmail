import { Language, Theme } from "$lib/types";
import { capitalize } from ".";

/**
 * Converts a locale string (e.g., "en-US") following the RFC 5646 standard
 * into a corresponding Language enum value (e.g., Language.EN_US).
 *
 * This function normalizes the input by converting it to uppercase and replacing
 * hyphens with underscores to match the enum key format.
 *
 * @param locale - A language tag string in RFC 5646 format (e.g., "en", "en-US", "en-GB").
 * @returns A matching Language enum value, or undefined if no match is found.
 */
export function convertToLanguageEnum(locale: string): Language | undefined {
    const enumKey = locale.replace("-", "_").toUpperCase();

    if (enumKey in Language) {
        return (Language as any)[enumKey];
    }

    return undefined;
}

export function convertToThemeEnum(theme: string): Theme | undefined {
    const enumKey = capitalize(theme);

    if (enumKey in Theme) {
        return (Theme as any)[enumKey];
    }

    return undefined;
}

export function convertToRFC5646Format(languageEnum: Language): string {
    const languageEnumKey = getEnumKeyByValue(Language, languageEnum);
    if (!languageEnumKey) return "";
    const [lang, region] = languageEnumKey.split("_");
    return `${lang.toLowerCase()}-${region.toUpperCase()}`;
}

export function getEnumKeyByValue<T extends Record<string, any>>(
    enumObj: T,
    value: any,
): keyof T | undefined {
    return Object.entries(enumObj).find((k) => k[1] === value)?.[0];
}

export function getEnumValueByKey<T extends Record<string, string>>(
    enumObj: T,
    key: keyof T,
): T[keyof T] {
    return enumObj[key];
}
