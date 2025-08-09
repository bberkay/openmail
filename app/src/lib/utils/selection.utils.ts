import { removeWhitespaces } from ".";

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
