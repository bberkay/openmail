export function simpleDeepCopy<T>(source: T): T {
    return JSON.parse(JSON.stringify(source));
}

export function isObjEmpty(obj: Record<string, any>): boolean {
    return Object.values(obj).every(
        (value) =>
            !!value === false || (Array.isArray(value) && value.length === 0),
    );
}

export function removeFalsyParamsAndEmptyLists(
    params: Record<string, any>,
): Record<string, string> {
    return Object.fromEntries(
        Object.entries(params).filter(([_, value]) => {
            if (Array.isArray(value)) {
                return value.length > 0;
            }
            return !!value;
        }),
    );
}
