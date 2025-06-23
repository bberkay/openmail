import { DEFAULT_LANGUAGE } from "$lib/constants";
import { local } from "$lib/locales";
import { Folder, Language, Size, Theme, type Account } from "$lib/types";

export function createDomElement(html: string): HTMLElement {
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    return template.content.firstElementChild as HTMLElement;
}

export function getMonths(): string[] {
    return [
        local.january[DEFAULT_LANGUAGE],
        local.february[DEFAULT_LANGUAGE],
        local.march[DEFAULT_LANGUAGE],
        local.april[DEFAULT_LANGUAGE],
        local.may[DEFAULT_LANGUAGE],
        local.june[DEFAULT_LANGUAGE],
        local.july[DEFAULT_LANGUAGE],
        local.august[DEFAULT_LANGUAGE],
        local.september[DEFAULT_LANGUAGE],
        local.october[DEFAULT_LANGUAGE],
        local.november[DEFAULT_LANGUAGE],
        local.december[DEFAULT_LANGUAGE],
    ];
}

export function getDays(): string[] {
    return [
        local.sun[DEFAULT_LANGUAGE],
        local.mon[DEFAULT_LANGUAGE],
        local.tue[DEFAULT_LANGUAGE],
        local.wed[DEFAULT_LANGUAGE],
        local.thu[DEFAULT_LANGUAGE],
        local.fri[DEFAULT_LANGUAGE],
        local.sat[DEFAULT_LANGUAGE],
    ];
}

export function isSameDay(date1: Date, date2: Date): boolean {
    return (
        date1.getUTCFullYear() === date2.getUTCFullYear() &&
        date1.getUTCMonth() === date2.getUTCMonth() &&
        date1.getUTCDate() === date2.getUTCDate()
    );
}

export function compactEmailDate(emailDateStr: string, strict = true) {
    const inputDate = new Date(emailDateStr);
    const currentDate = new Date();
    const months = getMonths();

    const hours = inputDate.getUTCHours().toString().padStart(2, "0");
    const minutes = inputDate.getUTCMinutes().toString().padStart(2, "0");
    const timeFormat = `${hours}:${minutes}`;

    const isToday = isSameDay(inputDate, currentDate);
    const isYesterday = isSameDay(
        inputDate,
        new Date(currentDate.getTime() - 86400000),
    ); // 24 hours in milliseconds

    const day = inputDate.getUTCDate();
    const month = months[inputDate.getUTCMonth()];
    const year = inputDate.getUTCFullYear();
    const currentYear = currentDate.getFullYear();

    if (strict && (isToday || isYesterday)) {
        return timeFormat;
    } else if (year === currentYear) {
        return `${day} ${month} ${timeFormat}`;
    } else {
        return `${day} ${month} ${year}`;
    }
}

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

export function debounce<T extends (...args: any[]) => any>(
    func: T,
    delay: number,
) {
    let timer: ReturnType<typeof setTimeout> | undefined;

    return (...args: Parameters<T>): void => {
        if (timer) {
            clearTimeout(timer);
        }

        timer = setTimeout(() => {
            func(...args);
        }, delay);
    };
}

export function simpleDeepCopy<T>(source: T): T {
    return JSON.parse(JSON.stringify(source));
}

export async function generateHash(data: any, algorithm?: AlgorithmIdentifier) {
    algorithm ??= 'SHA-256';
    const encoder = new TextEncoder();
    const dataBytes = encoder.encode(data);

    const hashBuffer = await window.crypto.subtle.digest(algorithm, dataBytes);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

export function combine(...strings: any[]): string {
    return strings.filter((str) => str !== undefined && str !== null).join(" ");
}

export function generateRandomId(): string {
    return Date.now().toString();
}

export function removeWhitespaces(text: string): string {
    return text.replace(/\s+/g, "");
}

export function isObjEmpty(obj: Record<string, any>): boolean {
    return Object.values(obj).every(
        (value) =>
            !!value === false || (Array.isArray(value) && value.length === 0),
    );
}

export function isUidInSelection(
    selection: string,
    searching: string,
): boolean {
    searching = removeWhitespaces(searching);
    if (
        selection.startsWith(searching + ",") ||
        selection.endsWith("," + searching)
    )
        return true;
    return selection.includes("," + searching + ",") || selection === searching;
}

/**
 * Sorts a string of comma-separated numbers and removes spaces
 * @param numbersString - A string containing numbers separated by commas and possibly spaces
 * @returns A sorted string of numbers without spaces, separated by commas
 */
export function sortSelection(numbersString: string): string {
    return numbersString
        .split(",")
        .map((part) => parseInt(part.trim(), 10))
        .sort((a, b) => a - b)
        .join(",");
}

export function isStandardFolder(
    folderName: string,
    targetStandardFolder?: Folder,
) {
    return (
        targetStandardFolder
            ? [targetStandardFolder]
            : Object.values(Folder)
    ).some((standardFolder) => {
        folderName = folderName.toLowerCase();
        standardFolder = standardFolder.toLowerCase() as Folder;
        return folderName.startsWith(standardFolder + ":") ||
            folderName === standardFolder;
    });
}

export function removeTrailingDelimiter(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return folderPath.endsWith(hierarchyDelimiter)
        ? folderPath.slice(0, -hierarchyDelimiter.length)
        : folderPath;
}

export function removeLeadingDelimiter(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return folderPath.startsWith(hierarchyDelimiter)
        ? folderPath.slice(hierarchyDelimiter.length)
        : folderPath;
}

export function trimDelimiters(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return removeLeadingDelimiter(
        removeTrailingDelimiter(folderPath, hierarchyDelimiter),
        hierarchyDelimiter,
    );
}

export function extractFolderName(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    const normalizedPath = removeTrailingDelimiter(
        folderPath,
        hierarchyDelimiter,
    );

    const lastDelimiterIndex = normalizedPath.lastIndexOf(hierarchyDelimiter);
    if (lastDelimiterIndex === -1) {
        return folderPath;
    }

    return folderPath.slice(lastDelimiterIndex);
}

export function isExactFolderMatch(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): boolean {
    if (folderPath === folderName) return true;

    if (folderName.includes(hierarchyDelimiter)) {
        return (
            trimDelimiters(folderPath, hierarchyDelimiter) ===
            trimDelimiters(folderName, hierarchyDelimiter)
        );
    }

    return extractFolderName(folderPath, hierarchyDelimiter) === folderName;
}

export function isSubfolderOrMatch(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): boolean {
    if (folderName.includes(hierarchyDelimiter)) {
        return isExactFolderMatch(folderPath, folderName, hierarchyDelimiter);
    }

    return folderPath.split(hierarchyDelimiter).includes(folderName);
}

export function removeFromPath(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): string {
    if (folderPath === folderName) return "";
    const index = folderPath.lastIndexOf(
        hierarchyDelimiter +
            removeLeadingDelimiter(folderPath, hierarchyDelimiter),
    );
    if (index === -1) return folderPath;

    return folderPath.slice(index);
}

export function replaceFolderName(
    folderPath: string,
    oldFolderName: string,
    newFolderName: string,
    hierarchyDelimiter: string,
): string {
    return folderPath
        .split(hierarchyDelimiter)
        .map((part) => {
            if (part === oldFolderName) return newFolderName;
            return part;
        })
        .join(hierarchyDelimiter);
}

export function isTopLevel(
    folderPath: string,
    hierarchyDelimiter: string,
): boolean {
    return trimDelimiters(folderPath, hierarchyDelimiter).includes(
        hierarchyDelimiter,
    );
}

export function removeFalsyParamsAndEmptyLists(
    params: Record<string, any>,
): Record<string, string> {
    return Object.fromEntries(
        Object.entries(params).filter(([_, value]) => {
            if (Array.isArray(value)) {
                return value.length > 0;
            }
            return !!value;
        }),
    );
}

export function makeSizeHumanReadable(bytes: number): string {
    const sizes: Size[] = Object.values(Size);
    if (bytes === 0) return "n/a";
    const i = Math.floor(Math.log2(bytes) / 10);
    return concatValueAndUnit(
        Math.round(bytes / Math.pow(2, i * 10)),
        sizes[i],
    );
}

export function convertSizeToBytes(size: [number, Size] | string): number {
    const sizeMultiplier: Record<Size, number> = {
        [Size.Bytes]: 1,
        [Size.KB]: 1024,
        [Size.MB]: 1024 ** 2,
    };

    const [humanSizeValue, humanSizeType] =
        typeof size === "string" ? parseValueAndUnit(size) : size;
    if (!humanSizeValue || !humanSizeType) {
        throw new Error("Invalid human-readable size format");
    }

    const multiplier = sizeMultiplier[humanSizeType as Size];
    if (!multiplier) {
        throw new Error(`Unsupported size type: ${humanSizeType}`);
    }

    return Math.round(multiplier * humanSizeValue);
}

export function parseValueAndUnit(size: string): [number, Size] {
    const [sizeValue, sizeUnit] = size.split(" ");
    return [parseFloat(sizeValue), sizeUnit as Size];
}

export function concatValueAndUnit(value: number | string, unit: Size): string {
    return `${typeof value === "string" ? parseFloat(value) : value} ${unit}`;
}

export function escapeHTML(str: string): string {
    return str
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

export function pulseTarget(target: HTMLElement): void {
    target.classList.add("pulse");
    target.addEventListener(
        "animationend",
        () => {
            target.classList.remove("pulse");
        },
        { once: true },
    );
}

export function shakeTarget(target: HTMLElement): void {
    target.classList.add("shake");
    target.addEventListener(
        "animationend",
        () => {
            target.classList.remove("shake");
        },
        { once: true },
    );
}

export function adjustSizes(
    smaller: string | [number, Size],
    larger: string | [number, Size],
    adjustToSmaller: boolean = true,
): [string | [number, Size], string | [number, Size]] {
    let [smallerValue, smallerUnit] =
        typeof smaller === "string" ? parseValueAndUnit(smaller) : smaller;
    let [largerValue, largerUnit] =
        typeof larger === "string" ? parseValueAndUnit(larger) : larger;

    if (
        convertSizeToBytes([smallerValue, smallerUnit]) <=
        convertSizeToBytes([largerValue, largerUnit])
    ) {
        if (adjustToSmaller) {
            largerValue = Math.max(smallerValue - 1, 0);
            largerUnit = smallerUnit;
        } else {
            smallerValue = largerValue + 1;
            smallerUnit = largerUnit;
        }
    }

    return [
        typeof smaller === "string"
            ? concatValueAndUnit(smallerValue, smallerUnit)
            : [smallerValue, smallerUnit],
        typeof larger === "string"
            ? concatValueAndUnit(largerValue, largerUnit)
            : [largerValue, largerUnit],
    ];
}

export function capitalize(s: string): string {
    return s && String(s[0]).toUpperCase() + String(s).slice(1).toLowerCase();
}

export function truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + "...";
}

export function isEmailValid(email: string): boolean {
    return (
        email.match(/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/) !== null
    );
}

export function swap<T extends unknown>(
    arr: T[],
    fromIndex: number,
    toIndex: number,
): T[] {
    if (
        fromIndex < 0 ||
        fromIndex >= arr.length ||
        toIndex < 0 ||
        toIndex >= arr.length
    ) {
        throw new Error("Index out of bounds");
    }

    [arr[fromIndex], arr[toIndex]] = [arr[toIndex], arr[fromIndex]];
    return arr;
}

export function convertToIMAPDate(dateStringOrDate: string | Date): string {
    const date =
        typeof dateStringOrDate === "string"
            ? new Date(dateStringOrDate)
            : dateStringOrDate;
    return `${date.getDate()}-${date.toLocaleString("en-GB", { month: "short" })}-${date.getFullYear()}`;
}

export function range(start: number, stop: number, step: number): number[] {
    return Array.from(
        { length: Math.ceil((stop - start) / step) },
        (_, i) => start + i * step,
    );
}

export function roundUpToMultiple(a: number, b: number): number {
    return Math.ceil(a / b) * b;
}

export function createSenderAddress(
    emailAddress: string,
    fullname: string | null = null,
): string {
    if (fullname && fullname.length > 0) return `${fullname} <${emailAddress}>`;
    return emailAddress;
}

export function createSenderAddressFromAccount(account: Account): string {
    return createSenderAddress(account.email_address, account.fullname);
}

export function extractFullname(sender: string): string {
    const match = sender.match(/^(.*?)<.*@.*>$/);
    return match ? match[1].trim() : "";
}

export function extractEmailAddress(sender: string): string {
    const match = sender.match(/<(.+@.+)>/);
    if (match) return match[1].trim();
    return sender.includes("@") ? sender.trim() : "";
}

export function addEmailToAddressList(
    e: Event,
    input: HTMLInputElement,
    addressList: string[],
) {
    if (e instanceof KeyboardEvent && (e.key === " " || e.key === "Spacebar")) {
        e.preventDefault();
    } else if (!(e instanceof FocusEvent || e instanceof MouseEvent)) {
        return;
    }

    const trimmedValue = input.value.trim();
    if (trimmedValue.length <= 0) return;

    if (!isEmailValid(extractEmailAddress(trimmedValue))) {
        pulseTarget(input);
        return;
    }

    addressList.push(trimmedValue);
    input.value = "";
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
