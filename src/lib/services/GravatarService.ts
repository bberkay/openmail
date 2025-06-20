import { createDomElement, extractEmailAddress, extractFullname, generateHash } from "$lib/utils";

const LOCAL_AVATAR_TEMPLATE = `
    <div style="background-color:{bg};color:{fg};text-align:center;">
        {shortenedName}
    </div>
`;
const GRAVATAR_IMAGE_TEMPLATE = `
    <img src="{gravatarUrl}" alt="Avatar of {fullname}">
`;

type ColorPair = { bg: string, fg: string };
const AVATAR_COLORS: ColorPair[] = [
    { bg: "#e583ce", fg: "#471033" },
    { bg: "#c8daf5", fg: "#20284b" },
    { bg: "#f4ff77", fg: "#4c2500" },
    { bg: "#dde8a0", fg: "#372b11" },
    { bg: "#99f6f0", fg: "#042b2f" },
    { bg: "#f0dfd8", fg: "#362119" },
    { bg: "#e8dfef", fg: "#2d1c36" },
    { bg: "#b4fee1", fg: "#003322" },
    { bg: "#9ef1da", fg: "#062d29" },
    { bg: "#b2d7ff", fg: "#09175d" },
    { bg: "#f8d2e2", fg: "#4b0c1b" },
    { bg: "#dad3ff", fg: "#290a6b" },
    { bg: "#fcd6cc", fg: "#43180c" },
];

type AvatarCache = { [senderAddress: string]: string };
const storedAvatars: AvatarCache = {};

export class GravatarService {
    public static getCachedAvatar(senderAddress: string): HTMLElement | undefined {
        const isAvatarStored = Object.hasOwn(storedAvatars, senderAddress);
        if (isAvatarStored) {
            return createDomElement(storedAvatars[senderAddress]);
        }

        return undefined;
    }

    public static getRandomAvatarColor(): ColorPair {
        return AVATAR_COLORS[Math.floor(Math.random() * AVATAR_COLORS.length)];
    }

    public static getAvatarInitials(senderAddress: string): string {
        let shortenedName = extractFullname(senderAddress);
        if (!shortenedName) {
            const emailAddress = extractEmailAddress(senderAddress);
            shortenedName = emailAddress.split("@")[0];
        }

        shortenedName = shortenedName.split(" ")[0][0].toUpperCase();
        return shortenedName;
    }

    public static createLocalAvatar(senderAddress: string) {
        const shortenedName = GravatarService.getAvatarInitials(senderAddress);
        const { bg,  fg } = GravatarService.getRandomAvatarColor();
        return createDomElement(
            LOCAL_AVATAR_TEMPLATE
                .replace("{shortenedName}", shortenedName)
                .replace("{bg}", bg)
                .replace("{fg}", fg)
        );
    }

    public static async fetchGravatar(senderAddress: string): Promise<HTMLElement | undefined> {
        const fullname = extractFullname(senderAddress);
        const emailAddress = extractEmailAddress(senderAddress);

        const hash = await generateHash(emailAddress.trim().toLowerCase());
        const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?d=404`;
        try {
            const response = await fetch(gravatarUrl);

            if (response.status !== 200) {
                return undefined;
            }

            return createDomElement(
                GRAVATAR_IMAGE_TEMPLATE
                    .replace("{gravatarUrl}", gravatarUrl)
                    .replace("{fullname}", fullname)
            )
        } catch {
            return undefined;
        }
    }

    public static async getAvatar(senderAddress: string): Promise<HTMLElement> {
        let avatar = GravatarService.getCachedAvatar(senderAddress);
        if (avatar) return avatar;

        avatar = await GravatarService.fetchGravatar(senderAddress);
        if (!avatar) {
            avatar = GravatarService.createLocalAvatar(senderAddress);
        }
        storedAvatars[senderAddress] = avatar.innerHTML;
        return avatar;
    }
}
