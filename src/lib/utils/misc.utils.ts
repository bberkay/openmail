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

export async function generateHash(data: any, algorithm?: AlgorithmIdentifier) {
    algorithm ??= 'SHA-256';
    const encoder = new TextEncoder();
    const dataBytes = encoder.encode(data);

    const hashBuffer = await window.crypto.subtle.digest(algorithm, dataBytes);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

export function generateRandomId(): string {
    return Date.now().toString();
}

export function roundUpToMultiple(a: number, b: number): number {
    return Math.ceil(a / b) * b;
}
