import { Size } from "./types";

export function makeSizeHumanReadable(bytes: number): string {
    const sizes: Size[] = Object.values(Size);
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

export function adjustSizes(smaller: [number, Size], larger: [number, Size], adjustToSmaller: boolean = true): [[number, Size], [number, Size]] {
    const multiplier = {
        [Size.Bytes]: 1,
        [Size.KB]: 1024,
        [Size.MB]: 1024 ** 2
    };

    let [smallerValue, smallerUnit] = smaller;
    let [largerValue, largerUnit] = larger;

    if (smallerValue * multiplier[smallerUnit] <= largerValue * multiplier[largerUnit]) {
        if (adjustToSmaller) {
            largerValue = Math.max(smallerValue - 1, 0);
            largerUnit = smallerUnit
        } else {
            smallerValue = largerValue + 1;
            smallerUnit = largerUnit
        }
    }

    return [[smallerValue, smallerUnit], [largerValue, largerUnit]];
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

export function convertHumanSizeToBytes(humanSize: string): number {
    const sizeMultiplier: Record<Size, number> = {
        [Size.Bytes]: 1,
        [Size.KB]: 1024,
        [Size.MB]: 1024 ** 2,
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
