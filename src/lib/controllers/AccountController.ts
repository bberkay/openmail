import { SharedStore } from "$lib/stores/shared.svelte";
import {
    ApiService,
    GetRoutes,
    PostRoutes,
    type GetResponse,
    type PostResponse,
    type BaseResponse,
} from "$lib/services/ApiService";
import { RSAEncryptor } from "$lib/services/RSAEncryptor";
import type { Account } from "$lib/types";

export class AccountController {
    public static async init(): Promise<BaseResponse> {
        const response = await AccountController.list();
        if (response.success && response.data) {
            SharedStore.accounts = response.data.connected;
            SharedStore.failedAccounts = response.data.failed;
        }

        return {
            success: response.success,
            message: response.success ? "Account Controller Initialized" : response.message
        }
    }

    public static async list(): Promise<GetResponse<GetRoutes.GET_ACCOUNTS>> {
        return await ApiService.get(SharedStore.server, GetRoutes.GET_ACCOUNTS);
    }

    public static async add(
        email_address: string,
        plain_password: string,
        fullname: string | null = null,
    ): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword =
            await encryptor.encryptPassword(plain_password);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.ADD_ACCOUNT,
            {
                email_address: email_address,
                fullname: fullname || undefined,
                encrypted_password: encryptedPassword,
            },
        );

        if (response.success) {
            SharedStore.accounts.push({
                email_address,
                ...(fullname && { fullname }),
            });
        }

        return response;
    }

    public static async edit(
        email_address: string,
        plain_password: string,
        fullname: string | null = null,
    ): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword =
            await encryptor.encryptPassword(plain_password);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.EDIT_ACCOUNT,
            {
                email_address: email_address,
                fullname: fullname || undefined,
                encrypted_password: encryptedPassword,
            },
        );

        if (response.success) {
            const target = SharedStore.accounts.findIndex(
                (account: Account) => account.email_address == email_address
            );
            SharedStore.accounts[target] = {
                email_address: email_address,
                ...(fullname && { fullname })
            }

            SharedStore.failedAccounts = SharedStore.failedAccounts.filter(
                (account: Account) => account.email_address !== email_address,
            );
        } else {
            if (
                SharedStore.failedAccounts.find(
                    (account: Account) => account.email_address !== email_address,
                )
            ) {
                SharedStore.failedAccounts.push({
                    email_address: email_address,
                    ...(fullname && { fullname }),
                });
            }
        }

        return response;
    }

    public static async remove(email_address: string): Promise<PostResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNT,
            {
                account: email_address,
            },
        );

        if (response.success) {
            SharedStore.accounts = SharedStore.accounts.filter(
                (item: Account) => item.email_address !== email_address,
            );
        }

        return response;
    }

    public static async removeAll(): Promise<PostResponse> {
        const response: PostResponse = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNTS,
            {},
        );

        if (response.success) {
            SharedStore.accounts = [];
        }

        return response;
    }
}
