import { ApiService, GetRoutes } from "./ApiService";

const RSA_ALGORITHM_NAME = "RSA-OAEP";
const RSA_HASH_ALGORITHM = "SHA-256";
const RSA_KEY_FORMAT = "spki";
const PEM_CLEANUP_REGEX = /(-----(BEGIN|END) PUBLIC KEY-----|\n)/g;

export class RSAEncryptor {
    private pemToArrayBuffer(pem: string) {
        const binary = atob(pem.replace(PEM_CLEANUP_REGEX, ""));
        const buffer = new ArrayBuffer(binary.length);
        const view = new Uint8Array(buffer);
        for (let i = 0; i < binary.length; i++) {
            view[i] = binary.charCodeAt(i);
        }
        return buffer;
    }

    private async getPublicKey(): Promise<CryptoKey> {
        const response = await ApiService.get(
            GetRoutes.GET_PUBLIC_KEY,
        );
        if (!response.success || !response.data)
            throw new Error("Failed to fetch public key");

        const publicKeyPem = this.pemToArrayBuffer(response.data.public_key);
        const publicKey = await window.crypto.subtle.importKey(
            RSA_KEY_FORMAT,
            publicKeyPem,
            {
                name: RSA_ALGORITHM_NAME,
                hash: { name: RSA_HASH_ALGORITHM },
            },
            true,
            ["encrypt"],
        );

        return publicKey;
    }

    public async encryptPassword(
        plaint_text_password: string,
    ): Promise<string> {
        const publicKey = await this.getPublicKey();

        const encoder = new TextEncoder();
        const encodedPassword = encoder.encode(plaint_text_password);
        const encryptedPassword = await window.crypto.subtle.encrypt(
            { name: RSA_ALGORITHM_NAME },
            publicKey,
            encodedPassword,
        );

        return btoa(String.fromCharCode(...new Uint8Array(encryptedPassword)));
    }
}
