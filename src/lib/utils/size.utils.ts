import { Size } from "$lib/types";

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
