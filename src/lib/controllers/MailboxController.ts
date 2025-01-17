import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes, type BaseResponse, type GetResponse } from "$lib/services/ApiService";
import { Folder } from "$lib/types";

export class MailboxController {
    public async getAllMailboxes(): Promise<GetResponse<GetRoutes.GET_MAILBOXES>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.accounts
                        .map((account) => account.email_address)
                        .join(",")
                }
            }
        );
    }

    public async updateAllMailboxes(): Promise<BaseResponse> {
        const response = await this.getAllMailboxes();

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
            SharedStore.currentFolder = response.data[0].result.folder;
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async getAllFolders(): Promise<GetResponse<GetRoutes.GET_FOLDERS>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: SharedStore.accounts
                        .map((account) => account.email_address)
                        .join(","),
                }
            }
        );
    }

    public async updateAllFolders(): Promise<BaseResponse> {
        const response = await this.getAllFolders();

        if (response.success && response.data) {
            const standardFolderList = Object.values(Folder).map(folder => folder.trim().toLowerCase() + ":");
            response.data.forEach((account, i) => {
                // Standard folders
                SharedStore.standardFolders[i] = {
                    email_address: account.email_address,
                    result: []
                };
                standardFolderList.forEach((standardFolder) => {
                    const matchedFolder = account.result.find(
                        currentFolder => currentFolder.trim().toLowerCase().startsWith(standardFolder)
                    );
                    if (matchedFolder)
                        SharedStore.standardFolders[i].result.push(matchedFolder);
                });

                // Custom folders
                SharedStore.customFolders[i] = {
                    email_address: account.email_address,
                    result: []
                };
                SharedStore.customFolders[i].result = account.result.filter((currentFolder) => {
                    return SharedStore.standardFolders[i].result.includes(currentFolder) !== true
                });
            })
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async getEmailContent(account: string, uid: string): Promise<GetResponse<GetRoutes.GET_EMAIL_CONTENT>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_EMAIL_CONTENT,
            {
                pathParams: {
                    accounts: account,
                    folder: encodeURIComponent(SharedStore.currentFolder),
                    uid: uid
                }
            }
        );
    }
}
