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
import { NotificationHandler } from "$lib/services/NotificationHandler";

export class AccountController {
    public static async init(): Promise<BaseResponse> {
        const response = await AccountController.list();
        if (response.success && response.data) {
            SharedStore.currentAccount = response.data.connected[0]; // TODO: Change this to "home"
            SharedStore.accounts = response.data.connected;
            SharedStore.failedAccounts = response.data.failed;
        }

        return {
            success: response.success,
            message: response.success
                ? "Account Controller Initialized"
                : response.message,
        };
    }

    public static async list(): Promise<GetResponse<GetRoutes.GET_ACCOUNTS>> {
        return await ApiService.get(GetRoutes.GET_ACCOUNTS);
    }

    private static async _initializeNotifications(email_address: string) {
        const acc = SharedStore.accounts.find(
            (acc) => acc.email_address === email_address,
        )!;
        SharedStore.notificationChannels[email_address] = new NotificationHandler(acc);

        if (SharedStore.preferences.notificationStatus instanceof Object) {
            SharedStore.preferences.notificationStatus[email_address] = true;
        }
    }

    public static async add(
        email_address: string,
        plain_password: string,
        fullname: string | null = null,
        initializeNotifications: boolean = false,
    ): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword =
            await encryptor.encryptPassword(plain_password);
        const response = await ApiService.post(PostRoutes.ADD_ACCOUNT, {
            email_address: email_address,
            fullname: fullname || undefined,
            encrypted_password: encryptedPassword,
        });

        if (response.success) {
            SharedStore.accounts.push({
                email_address,
                ...(fullname && { fullname }),
            });

            if (initializeNotifications) {
                AccountController._initializeNotifications(email_address);
            }
        }

        return response;
    }

    private static async _reinitializeNotifications(email_address: string) {
        if (Object.hasOwn(SharedStore.notificationChannels, email_address)) {
            SharedStore.notificationChannels[email_address].reinitialize();
        }
    }

    public static async edit(
        email_address: string,
        plain_password: string,
        fullname: string | null = null,
    ): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword =
            await encryptor.encryptPassword(plain_password);

        const response = await ApiService.post(PostRoutes.EDIT_ACCOUNT, {
            email_address: email_address,
            fullname: fullname || undefined,
            encrypted_password: encryptedPassword,
        });

        if (response.success) {
            const target = SharedStore.accounts.findIndex(
                (account: Account) => account.email_address == email_address,
            );

            SharedStore.accounts[target] = {
                email_address: email_address,
                ...(fullname && { fullname }),
            };

            SharedStore.failedAccounts = SharedStore.failedAccounts.filter(
                (account: Account) => account.email_address !== email_address,
            );

            AccountController._reinitializeNotifications(email_address);
        } else {
            if (
                SharedStore.failedAccounts.find(
                    (account: Account) =>
                        account.email_address !== email_address,
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

    private static async _terminateNotifications(email_address: string) {
        if (Object.hasOwn(SharedStore.notificationChannels, email_address)) {
            SharedStore.notificationChannels[email_address].terminate();
            delete SharedStore.notificationChannels[email_address];
        }

        if (
            SharedStore.preferences.notificationStatus instanceof Object &&
            Object.hasOwn(
                SharedStore.preferences.notificationStatus,
                email_address,
            )
        ) {
            delete SharedStore.preferences.notificationStatus[email_address];
        }
    }

    public static async remove(
        email_address: string,
    ): Promise<PostResponse> {
        const response = await ApiService.post(PostRoutes.REMOVE_ACCOUNT, {
            account: email_address,
        });

        if (response.success) {
            AccountController._terminateNotifications(email_address);
            SharedStore.accounts = SharedStore.accounts.filter(
                (item: Account) => item.email_address !== email_address,
            );
        }

        return response;
    }

    public static async removeAll(): Promise<PostResponse> {
        const response: PostResponse = await ApiService.post(
            PostRoutes.REMOVE_ACCOUNTS,
            {},
        );

        if (response.success) {
            SharedStore.accounts.forEach((acc) =>
                AccountController._terminateNotifications(
                    acc.email_address,
                ),
            );
            SharedStore.accounts = [];
        }

        return response;
    }
}
