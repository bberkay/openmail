export function makeSizeHumanReadable(bytes: number): string {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    if (bytes === 0) return "n/a";
    const i = Math.floor(Math.log2(bytes) / 10);
    return Math.round(bytes / Math.pow(2, i * 10)) + " " + sizes[i];
}

export function createDomObject(html: string): HTMLElement | null {
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
