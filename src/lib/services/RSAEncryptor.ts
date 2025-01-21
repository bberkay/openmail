import { ApiService, GetRoutes } from "./ApiService";
import { SharedStore } from "$lib/stores/shared.svelte";

export class RSAEncryptor {
    private pemToArrayBuffer(pem: string) {
        const binary = atob(
            pem.replace(/(-----(BEGIN|END) PUBLIC KEY-----|\n)/g, ""),
        );
        const buffer = new ArrayBuffer(binary.length);
        const view = new Uint8Array(buffer);
        for (let i = 0; i < binary.length; i++) {
            view[i] = binary.charCodeAt(i);
        }
        return buffer;
    }

    private async getPublicKey(): Promise<CryptoKey> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_PUBLIC_KEY,
        );
        if (!response.success || !response.data)
            throw new Error("Failed to fetch public key");

        const publicKeyPem = this.pemToArrayBuffer(response.data.public_key);
        const publicKey = await window.crypto.subtle.importKey(
            "spki",
            publicKeyPem,
            {
                name: "RSA-OAEP",
                hash: { name: "SHA-256" },
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
            { name: "RSA-OAEP" },
            publicKey,
            encodedPassword,
        );

        return btoa(String.fromCharCode(...new Uint8Array(encryptedPassword)));
    }
}
