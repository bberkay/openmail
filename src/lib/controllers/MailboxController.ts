import { SharedStore } from "$lib/stores/shared.svelte";
import { ApiService, GetRoutes, type BaseResponse, type GetResponse, PostRoutes, type PostResponse } from "$lib/services/ApiService";
import { Folder, Mark, type EmailSummary } from "$lib/types";

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

    public async sendEmail(formData: FormData): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.SEND_EMAIL,
            formData
        );
    }

    public async paginateEmails(offset_start: number, offset_end: number): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.accounts.map((account) => account.email_address).join(", "),
                    offset_start: offset_start,
                    offset_end: offset_end,
                }
            }
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async refreshMailbox(): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.accounts[0].email_address
                },
                queryParams: {
                    folder: SharedStore.currentFolder
                }
            }
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async deleteEmails(selection: string[]): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                sequence_set: selection.includes("*") ? "1:*" : selection.join(","),
                folder: SharedStore.currentFolder
            }
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async moveEmails(selection: string[], destinationFolder: string): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                sequence_set: selection.includes("*") ? "1:*" : selection.join(","),
                source_folder: SharedStore.currentFolder,
                destination_folder: destinationFolder
            }
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async copyEmails(selection: string[], destinationFolder: string): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.COPY_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                sequence_set: selection.includes("*") ? "1:*" : selection.join(","),
                source_folder: SharedStore.currentFolder,
                destination_folder: destinationFolder
            }
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async markEmails(selection: string[], mark: string | Mark): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MARK_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                mark: mark,
                sequence_set: selection.includes("*") ? "1:*" : selection.join(","),
                folder: SharedStore.currentFolder
            }
        );

        if (response.success) {
            selection.forEach((uid: string) => {
                SharedStore.mailboxes[0].result.emails.forEach((email: EmailSummary) => {
                    if (email.uid === uid && Object.hasOwn(email, "flags") && email.flags) {
                        email.flags.push(mark);
                    }
                })
            })
        }

        return {
            success: response.success,
            message: response.message
        }
    }

    public async unmarkEmails(selection: string[], mark: string | Mark): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.UNMARK_EMAIL,
            {
                account: SharedStore.accounts.map((account) => account.email_address).join(", "),
                mark: mark,
                sequence_set: selection.includes("*") ? "1:*" : selection.join(","),
                folder: SharedStore.currentFolder
            }
        );

        if (response.success) {
            selection.forEach((uid: string) => {
                SharedStore.mailboxes[0].result.emails.forEach((email: EmailSummary) => {
                    if (email.uid === uid && Object.hasOwn(email, "flags") && email.flags) {
                        email.flags = email.flags.filter((flag: string) => flag !== mark);
                    }
                })
            })
        }

        return {
            success: response.success,
            message: response.message
        }
    }
}
