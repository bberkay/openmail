import { Folder } from "$lib/types";

export function isStandardFolder(
    folderName: string,
    targetStandardFolder?: Folder,
) {
    return (
        targetStandardFolder
            ? [targetStandardFolder]
            : Object.values(Folder)
    ).some((standardFolder) => {
        folderName = folderName.toLowerCase();
        standardFolder = standardFolder.toLowerCase() as Folder;
        return folderName.startsWith(standardFolder + ":") ||
            folderName === standardFolder;
    });
}

export function removeTrailingDelimiter(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return folderPath.endsWith(hierarchyDelimiter)
        ? folderPath.slice(0, -hierarchyDelimiter.length)
        : folderPath;
}

export function removeLeadingDelimiter(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return folderPath.startsWith(hierarchyDelimiter)
        ? folderPath.slice(hierarchyDelimiter.length)
        : folderPath;
}

export function trimDelimiters(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    return removeLeadingDelimiter(
        removeTrailingDelimiter(folderPath, hierarchyDelimiter),
        hierarchyDelimiter,
    );
}

export function extractFolderName(
    folderPath: string,
    hierarchyDelimiter: string,
): string {
    const normalizedPath = removeTrailingDelimiter(
        folderPath,
        hierarchyDelimiter,
    );

    const lastDelimiterIndex = normalizedPath.lastIndexOf(hierarchyDelimiter);
    if (lastDelimiterIndex === -1) {
        return folderPath;
    }

    return folderPath.slice(lastDelimiterIndex);
}

export function isExactFolderMatch(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): boolean {
    if (folderPath === folderName) return true;

    if (folderName.includes(hierarchyDelimiter)) {
        return (
            trimDelimiters(folderPath, hierarchyDelimiter) ===
            trimDelimiters(folderName, hierarchyDelimiter)
        );
    }

    return extractFolderName(folderPath, hierarchyDelimiter) === folderName;
}

export function isSubfolderOrMatch(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): boolean {
    if (folderName.includes(hierarchyDelimiter)) {
        return isExactFolderMatch(folderPath, folderName, hierarchyDelimiter);
    }

    return folderPath.split(hierarchyDelimiter).includes(folderName);
}

export function removeFromPath(
    folderPath: string,
    folderName: string,
    hierarchyDelimiter: string,
): string {
    if (folderPath === folderName) return "";
    const index = folderPath.lastIndexOf(
        hierarchyDelimiter +
            removeLeadingDelimiter(folderPath, hierarchyDelimiter),
    );
    if (index === -1) return folderPath;

    return folderPath.slice(index);
}

export function replaceFolderName(
    folderPath: string,
    oldFolderName: string,
    newFolderName: string,
    hierarchyDelimiter: string,
): string {
    return folderPath
        .split(hierarchyDelimiter)
        .map((part) => {
            if (part === oldFolderName) return newFolderName;
            return part;
        })
        .join(hierarchyDelimiter);
}

export function isTopLevel(
    folderPath: string,
    hierarchyDelimiter: string,
): boolean {
    return trimDelimiters(folderPath, hierarchyDelimiter).includes(
        hierarchyDelimiter,
    );
}
