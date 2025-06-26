import { generateHash } from "$lib/utils";
import { type Gravatar, type LocalAvatar } from "$lib/types";
import { PreferencesStore } from "$lib/stores/PreferencesStore";

const GRAVATAR_URL = "https://gravatar.com/avatar/";

const BASE_AVATAR_CSS = `
    display: flex;
    align-items: center;
    justify-content: center;
    width: var(--font-size-lg);
    height: var(--font-size-lg);
    border-radius: var(--radius-sm);
`;

const LOCAL_AVATAR_TEMPLATE = `
    <div
        class="local-avatar"
        style="
            ${BASE_AVATAR_CSS}
            background-color: {bg};
            color: {fg};
        "
    >
        {initials}
    </div>
`;
const GRAVATAR_TEMPLATE = `
    <img
        class="gravatar"
        src="{gravatarUrlWithHash}"
        alt="{fullname}"
        style="
            ${BASE_AVATAR_CSS}
        "
    />
`;
const SKELETON_AVATAR_TEMPLATE = `
    <div
        class="skeleton-avatar"
        style="
            ${BASE_AVATAR_CSS}
            background-color: #c2cdca;
        "
    >
    </div>
`;

type AvatarColorPair = { bg: string; fg: string };
const AVATAR_COLORS: AvatarColorPair[] = [
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
    { bg: "#c2cdca", fg: "#171c1c" },
];

type EmailAddress = string;
const MAX_CACHE_LENGTH = 100;
const storedAvatars: Map<EmailAddress, Gravatar | LocalAvatar> = new Map();

export class GravatarService {
    public static getCachedAvatar(
        email_address: string,
    ): Gravatar | LocalAvatar | undefined {
        return storedAvatars.get(email_address);
    }

    private static _checkCacheSize(): void {
        if (storedAvatars.size > MAX_CACHE_LENGTH) {
            const iterator = storedAvatars.keys();
            const reducedLength = Math.max(
                storedAvatars.size - Number(PreferencesStore.mailboxLength),
                0,
            );
            for (let i = 0; i < reducedLength; i++) {
                const next = iterator.next();
                if (next.done) break;
                storedAvatars.delete(next.value);
            }
        }
    }

    private static _saveToCache(
        email_address: string,
        avatar: Gravatar | LocalAvatar,
    ) {
        GravatarService._checkCacheSize();
        storedAvatars.set(email_address, avatar);
    }

    private static _getRandomAvatarColor(): AvatarColorPair {
        return AVATAR_COLORS[Math.floor(Math.random() * AVATAR_COLORS.length)];
    }

    private static _getAvatarInitials(
        email_address: string,
        fullname?: string,
    ): string {
        return (fullname || email_address).split(" ")[0][0].toUpperCase();
    }

    private static _createLocalAvatar(
        email_address: string,
        fullname?: string,
    ): LocalAvatar {
        const initials = GravatarService._getAvatarInitials(
            fullname || email_address,
        );
        const { bg, fg } = GravatarService._getRandomAvatarColor();
        const localAvatar = { bg, fg, initials };
        GravatarService._saveToCache(email_address, localAvatar);
        return localAvatar;
    }

    private static async _fetchGravatar(
        email_address: string,
        fullname?: string,
    ): Promise<Gravatar | undefined> {
        const hash = await generateHash(email_address.trim().toLowerCase());
        const gravatarUrlWithHash = GRAVATAR_URL + hash;
        try {
            const response = await fetch(gravatarUrlWithHash + "?d=404");
            if (response.status !== 200) return undefined;
            const gravatar = { hash, fullname };
            GravatarService._saveToCache(email_address, gravatar);
            return gravatar;
        } catch {
            return undefined;
        }
    }

    public static renderLocalAvatar(localAvatar: LocalAvatar): string {
        return LOCAL_AVATAR_TEMPLATE.replace("{initials}", localAvatar.initials)
            .replace("{bg}", localAvatar.bg)
            .replace("{fg}", localAvatar.fg);
    }

    public static renderGravatar(gravatar: Gravatar): string {
        return GRAVATAR_TEMPLATE.replace(
            "{gravatarUrlWithHash}",
            GRAVATAR_URL + gravatar.hash,
        ).replace("{fullname}", gravatar.fullname || "");
    }

    public static renderSkeletonAvatar(): string {
        return SKELETON_AVATAR_TEMPLATE;
    }

    public static renderAvatarData(
        avatarData: Gravatar | LocalAvatar,
    ): string {
        if (!Object.hasOwn(avatarData, "initials")) {
            const gravatar = avatarData as Gravatar;
            return GravatarService.renderGravatar(gravatar);
        } else {
            const localAvatar = avatarData as LocalAvatar;
            return GravatarService.renderLocalAvatar(localAvatar);
        }
    }

    public static async createAvatarData(
        email_address: string,
        fullname?: string,
    ): Promise<Gravatar | LocalAvatar> {
        let avatar = GravatarService.getCachedAvatar(email_address);
        if (avatar) return avatar;

        avatar = await GravatarService._fetchGravatar(email_address, fullname);
        if (!avatar) {
            avatar = GravatarService._createLocalAvatar(email_address, fullname);
        }

        return avatar;
    }

    public static async getAvatarHTML(
        email_address: string,
        fullname?: string,
    ): Promise<string> {
        const avatarData = await GravatarService.createAvatarData(
            email_address,
            fullname,
        );
        return GravatarService.renderAvatarData(avatarData);
    }
}
