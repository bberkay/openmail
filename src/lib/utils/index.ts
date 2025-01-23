import { Size } from "./types";

export function createDomObject(html: string): HTMLElement {
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    return template.content.firstElementChild as HTMLElement;
}

export function debounce(func: Function, delay: number) {
    let timer = -1;
    return (...args: any) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func(...args);
        }, delay);
    };
}

export function removeWhitespaces(text: string): string {
    return text.replace(/\s+/g, '');
}

export function isObjEmpty(obj: Record<string, any>): boolean {
    return Object.values(obj).every(
        (value) => !!value === false || (Array.isArray(value) && value.length === 0)
    );
}

export function removeFalsyParamsAndEmptyLists(
    params: Record<string, any>
): Record<string, string> {
    return Object.fromEntries(
        Object.entries(params).filter(([_, value]) => {
            if (Array.isArray(value)) {
                return value.length > 0;
            }
            return !!value;
        })
    );
}

export function makeSizeHumanReadable(bytes: number): string {
    const sizes: Size[] = Object.values(Size);
    if (bytes === 0) return "n/a";
    const i = Math.floor(Math.log2(bytes) / 10);
    return concatValueAndUnit(Math.round(bytes / Math.pow(2, i * 10)), sizes[i]);
}

export function convertSizeToBytes(size: [number, Size] | string): number {
    const sizeMultiplier: Record<Size, number> = {
        [Size.Bytes]: 1,
        [Size.KB]: 1024,
        [Size.MB]: 1024 ** 2,
    };

    const [humanSizeValue, humanSizeType] = typeof size === "string" ? parseValueAndUnit(size) : size;
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

export function adjustSizes(smaller: string | [number, Size], larger: string | [number, Size], adjustToSmaller: boolean = true): [string | [number, Size], string | [number, Size]]  {
    let [smallerValue, smallerUnit] = typeof smaller === "string" ? parseValueAndUnit(smaller) : smaller;
    let [largerValue, largerUnit] = typeof larger === "string" ? parseValueAndUnit(larger) : larger;

    if (convertSizeToBytes([smallerValue, smallerUnit]) <= convertSizeToBytes([largerValue, largerUnit])) {
        if (adjustToSmaller) {
            largerValue = Math.max(smallerValue - 1, 0);
            largerUnit = smallerUnit
        } else {
            smallerValue = largerValue + 1;
            smallerUnit = largerUnit
        }
    }

    return [
        typeof smaller === "string" ? concatValueAndUnit(smallerValue, smallerUnit) : [smallerValue, smallerUnit],
        typeof larger === "string" ? concatValueAndUnit(largerValue, largerUnit) : [largerValue, largerUnit]
    ];
}

export function capitalize(s: string): string {
    return s && String(s[0]).toUpperCase() + String(s).slice(1).toLowerCase();
}

export function isEmailValid(email: string): boolean {
    return email.match(
        /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/,
    ) !== null;
}

export function swap<T extends unknown>(arr: T[], fromIndex: number, toIndex: number): T[] {
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
    const date = typeof dateStringOrDate == "string" ? new Date(dateStringOrDate) : dateStringOrDate;
    return date
        .toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
        .replace(',', '');
}

export function range(start: number, stop: number, step: number): number[] {
    return Array.from(
        { length: Math.ceil((stop - start) / step) },
        (_, i) => start + i * step,
    );
}

export function getMonths(): string[] {
    return [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ];
}
