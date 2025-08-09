export function createDomElement(html: string): HTMLElement {
    const template = document.createElement("template");
    template.innerHTML = html.trim();
    return template.content.firstElementChild as HTMLElement;
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
