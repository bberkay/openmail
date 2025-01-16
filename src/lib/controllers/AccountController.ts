import { SharedStore, SharedStoreKeys } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes, PostRoutes, type GetResponse, type PostResponse, type BaseResponse } from "$lib/services/ApiService";
import { RSAEncryptor } from "$lib/services/RSAEncryptor";

export class AccountController {
    public async list(): Promise<GetResponse<GetRoutes.GET_ACCOUNTS>> {
        return await ApiService.get(SharedStore.server, GetRoutes.GET_ACCOUNTS);
    }

    public async update(): Promise<BaseResponse> {
        const response = await ApiService.get(SharedStore.server, GetRoutes.GET_ACCOUNTS);
        if (response.success && response.data) {
            SharedStore.accounts = response.data;
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async add(email_address: string, plain_password: string, fullname: string | null = null): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword = await encryptor.encryptPassword(plain_password);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.ADD_ACCOUNT,
            {
                email_address: email_address,
                fullname: fullname || undefined,
                encrypted_password: encryptedPassword
            }
        );

        if(response.success){
            SharedStore.accounts.push({
                email_address,
                ...(fullname && { fullname }),
            });
        }

        return response;
    }

    public async edit(email_address: string, plain_password: string, fullname: string | null = null): Promise<PostResponse> {
        const encryptor = new RSAEncryptor();
        const encryptedPassword = await encryptor.encryptPassword(plain_password);
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.EDIT_ACCOUNT,
            {
                email_address: email_address,
                fullname: fullname || undefined,
                encrypted_password: encryptedPassword
            }
        );

        if(response.success){
            SharedStore.accounts.push({
                email_address: email_address,
                ...(fullname && { fullname })
            });

            SharedStore.failedAccounts = SharedStore.failedAccounts.filter(
                (item) => item.email_address !== email_address
            );
        } else {
            if (SharedStore.failedAccounts.find((item) => item.email_address !== email_address)) {
                SharedStore.failedAccounts.push({
                    email_address: email_address,
                    ...(fullname && { fullname })
                });
            }
        }

        return response;
    }

    public async remove(account: string): Promise<PostResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNT,
            {
                account: account
            }
        );

        if (response.success) {
            SharedStore.accounts = SharedStore.accounts.filter((item) => item.email_address !== account);
        }

        return response;
    }

    public async removeAll(): Promise<PostResponse> {
        const response: PostResponse = await ApiService.post(
            SharedStore.server,
            PostRoutes.REMOVE_ACCOUNTS,
            {},
        );

        if (response.success) {
            SharedStore.reset(SharedStoreKeys.accounts);
        }

        return response;
    }
}
