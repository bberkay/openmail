import { type Size } from "./types";

export function makeSizeHumanReadable(bytes: number): string {
    const sizes: Size[] = ["Bytes", "KB", "MB", "GB"];
    if (bytes === 0) return "n/a";
    const i = Math.floor(Math.log2(bytes) / 10);
    return Math.round(bytes / Math.pow(2, i * 10)) + " " + sizes[i];
}

export function createDomObject(html: string): HTMLElement {
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    return template.content.firstElementChild as HTMLElement;
}

export function countCharacter(str: string, char: string): number {
    let count = 0;
    for (const c of str) {
        if (c === char) {
            count++;
        }
    }
    return count;
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

export function addDays(dateString: string, days: number): string {
    const date = new Date(dateString);
    date.setDate(date.getDate() + days);
    return date.toISOString().split("T")[0];
}

export function capitalize(s: string): string {
    return s && String(s[0]).toUpperCase() + String(s).slice(1).toLowerCase();
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

export function convertHumanSizeToBytes(humanSize: string): number {
    const sizeMultiplier: Record<Size, number> = {
        "Bytes": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 100 ** 3
    };

    const [humanSizeValue, humanSizeType] = humanSize.split(" ");
    if (!humanSizeValue || !humanSizeType) {
        throw new Error("Invalid human-readable size format");
    }

    const multiplier = sizeMultiplier[humanSizeType as Size];
    if (!multiplier) {
        throw new Error(`Unsupported size type: ${humanSizeType}`);
    }

    return Math.round(multiplier * parseFloat(humanSizeValue));
}

export function convertToIMAPDate(dateStringOrDate: string | Date): string {
    const date = typeof dateStringOrDate == "string" ? new Date(dateStringOrDate) : dateStringOrDate;
    return date
        .toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
        .replace(',', '');
}
