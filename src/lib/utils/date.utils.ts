import { DEFAULT_LANGUAGE } from "$lib/constants";
import { local } from "$lib/locales";

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

export function convertToIMAPDate(dateStringOrDate: string | Date): string {
    const date =
        typeof dateStringOrDate === "string"
            ? new Date(dateStringOrDate)
            : dateStringOrDate;
    return `${date.getDate()}-${date.toLocaleString("en-GB", { month: "short" })}-${date.getFullYear()}`;
}
