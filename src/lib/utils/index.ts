export function makeSizeHumanReadable(bytes: number) {
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    if (bytes === 0) return "n/a";
    const i = Math.floor(Math.log2(bytes) / 10);
    return Math.round(bytes / Math.pow(2, i * 10)) + " " + sizes[i];
}

export function createDomObject(html: string) {
    const template = document.createElement("template");
    template.innerHTML = html;
    return template.content.childNodes;
}
