import { SharedStore } from "$lib/stores/shared.svelte";
import {
    ApiService,
    GetRoutes,
    type BaseResponse,
    type GetResponse,
    PostRoutes,
    type PostResponse,
} from "$lib/services/ApiService";
import {
    Folder,
    Mark,
    type Account,
    type EmailSummary,
    type SearchCriteria,
} from "$lib/types";


export class MailboxController {
    private _get_accounts(accounts: Account [] | null = null): string {
        return (accounts || SharedStore.accounts)
            .map((account) => account.email_address)
            .join(",")
    }

    public async init(): Promise<BaseResponse> {
        let response;

        response = await this.getFolders();
        if (!response.success) {
            return {
                success: response.success,
                message: response.message
            }
        }

        response = await this.getMailboxes();
        return {
            success: response.success,
            message: response.success ? "Mailbox Controller Initialized" : response.message
        }
    }

    public async getMailboxes(accounts: Account[] | null = null): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: this._get_accounts(accounts),
                },
            },
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async getFolders(accounts: Account[] | null = null): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: this._get_accounts(accounts)
                },
            },
        );

        if (response.success && response.data) {
            const standardFolderList = Object.values(Folder).map(
                (folder) => folder.trim().toLowerCase() + ":",
            );

            // Extract standard and custom folders from data
            response.data.forEach((account, i) => {
                // Standard folders
                const standardFolders = SharedStore.standardFolders.find(
                    item => item.email_address === account.email_address
                );
                if (!standardFolders)
                    return;

                standardFolderList.forEach((standardFolder) => {
                    const matchedFolder = account.result.find((currentFolder) =>
                        currentFolder
                            .trim()
                            .toLowerCase()
                            .startsWith(standardFolder),
                    );
                    if (matchedFolder) {
                        standardFolders.result.push(matchedFolder);
                    }
                });

                // Custom folders
                const customFolders = SharedStore.customFolders.find(
                    item => item.email_address === account.email_address
                );
                if (!customFolders)
                    return;

                customFolders.result = account.result.filter(
                    (currentFolder) => {
                        return (
                            standardFolders.result.includes(
                                currentFolder,
                            ) !== true
                        );
                    },
                );
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async sendEmail(formData: FormData): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.SEND_EMAIL,
            formData,
        );
    }

    public async searchEmails(
        accounts: Account[],
        folder: Folder | string,
        searchCriteria: SearchCriteria | string | undefined = undefined,
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: this._get_accounts(accounts)
                },
                queryParams: {
                    folder: folder,
                    search:
                        typeof searchCriteria !== "string"
                            ? JSON.stringify(searchCriteria)
                            : searchCriteria,
                },
            },
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async paginateEmails(
        offset_start: number,
        offset_end: number,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError

        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.currentAccount.email_address,
                    offset_start: offset_start,
                    offset_end: offset_end,
                },
            },
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async getEmailContent(
        account: string,
        folder: string,
        uid: string,
    ): Promise<GetResponse<GetRoutes.GET_EMAIL_CONTENT>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_EMAIL_CONTENT,
            {
                pathParams: {
                    accounts: account,
                    folder: encodeURIComponent(folder),
                    uid: uid,
                },
            },
        );
    }

    public async deleteEmails(selection: string[]): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError
        if (!SharedStore.currentFolder)
            throw CurrentFolderIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: SharedStore.currentAccount.email_address,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: SharedStore.currentFolder,
            },
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async moveEmails(
        selection: string[],
        destinationFolder: string,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError
        if (!SharedStore.currentFolder)
            throw CurrentFolderIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_EMAIL,
            {
                account: SharedStore.currentAccount.email_address,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                source_folder: SharedStore.currentFolder,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async copyEmails(
        selection: string[],
        destinationFolder: string,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError
        if (!SharedStore.currentFolder)
            throw CurrentFolderIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.COPY_EMAIL,
            {
                account: SharedStore.currentAccount.email_address,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                source_folder: SharedStore.currentFolder,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            this.refreshMailbox();
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async markEmails(
        selection: string[],
        mark: string | Mark,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError
        if (!SharedStore.currentFolder)
            throw CurrentFolderIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MARK_EMAIL,
            {
                account: SharedStore.currentAccount.email_address,
                mark: mark,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: SharedStore.currentFolder,
            },
        );

        if (response.success) {
            selection.forEach((uid: string) => {
                SharedStore.mailboxes[0].result.emails.forEach(
                    (email: EmailSummary) => {
                        if (
                            email.uid === uid &&
                            Object.hasOwn(email, "flags") &&
                            email.flags
                        ) {
                            email.flags.push(mark);
                        }
                    },
                );
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async unmarkEmails(
        selection: string[],
        mark: string | Mark,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError
        if (!SharedStore.currentFolder)
            throw CurrentFolderIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.UNMARK_EMAIL,
            {
                account: SharedStore.currentAccount.email_address,
                mark: mark,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: SharedStore.currentFolder,
            },
        );

        if (response.success) {
            selection.forEach((uid: string) => {
                SharedStore.mailboxes[0].result.emails.forEach(
                    (email: EmailSummary) => {
                        if (
                            email.uid === uid &&
                            Object.hasOwn(email, "flags") &&
                            email.flags
                        ) {
                            email.flags = email.flags.filter(
                                (flag: string) => flag !== mark,
                            );
                        }
                    },
                );
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async createFolder(
        folderName: string,
        parentFolder: string | undefined,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.CREATE_FOLDER,
            {
                account: SharedStore.currentAccount.email_address,
                folder_name: folderName,
                parent_folder: parentFolder,
            },
        );

        if (response.success) {
            SharedStore.customFolders[0].result.push(
                parentFolder ? `${parentFolder}/${folderName}` : folderName,
            );
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async moveFolder(
        folderName: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_FOLDER,
            {
                account: SharedStore.currentAccount.email_address,
                folder_name: folderName,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            SharedStore.customFolders[0].result =
                SharedStore.customFolders[0].result.filter(
                    (e) => e !== folderName,
                );

            let newFolderPath = `${destinationFolder}/${folderName}`;
            if (folderName.includes("/")) {
                const tempLastIndex = folderName.lastIndexOf("/");
                const parentFolder = folderName.slice(0, tempLastIndex);
                if (
                    SharedStore.customFolders[0].result.includes(parentFolder)
                ) {
                    newFolderPath = `${destinationFolder}/${folderName.slice(tempLastIndex + 1)}`;
                }
            }
            SharedStore.customFolders[0].result.push(newFolderPath);
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async renameFolder(
        folderPath: string,
        newFolderName: string,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RENAME_FOLDER,
            {
                account: SharedStore.currentAccount.email_address,
                folder_name: folderPath,
                new_folder_name: newFolderName,
            },
        );

        if (response.success) {
            SharedStore.customFolders[0].result =
                SharedStore.customFolders[0].result.map((currentFolderName) => {
                    return currentFolderName.replace(
                        folderPath.includes("/")
                            ? folderPath.slice(folderPath.lastIndexOf("/") + 1)
                            : folderPath,
                        newFolderName,
                    );
                });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public async deleteFolder(
        folderName: string,
        subfolders: boolean,
    ): Promise<BaseResponse> {
        if (!SharedStore.currentAccount)
            throw CurrentAccountIsNotSelectedError

        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_FOLDER,
            {
                account: SharedStore.currentAccount.email_address,
                folder_name: folderName,
                subfolders: subfolders,
            },
        );

        if (response.success) {
            SharedStore.customFolders[0].result =
                SharedStore.customFolders[0].result.filter(
                    (e) =>
                        (e !== folderName && !subfolders) ||
                        !e.includes(folderName),
                );
        }

        return {
            success: response.success,
            message: response.message,
        };
    }
}
