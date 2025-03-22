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
    type Email,
    type SearchCriteria,
} from "$lib/types";
import { removeWhitespaces } from "$lib/utils";


export class MailboxController {
    private static _get_accounts(accounts: Account | Account[] | string[] | null = null): string {
        if (accounts && !Array.isArray(accounts)) {
            accounts = [accounts];
        }

        return (accounts && accounts.length > 0 ? accounts : SharedStore.accounts)
            .map((account) => {
                return typeof account !== "string"
                    ? account.email_address
                    : account
            }).join(",");
    }

    public static async init(): Promise<BaseResponse> {
        let response;
        response = await MailboxController.getFolders();
        if (!response.success) {
            return {
                success: response.success,
                message: response.message
            }
        }

        response = await MailboxController.getMailboxes(
            SharedStore.accounts,
            Folder.Inbox,
            {
                excluded_flags: [Mark.Seen],
            }
        );
        return {
            success: response.success,
            message: response.success ? "Mailbox Controller Initialized" : response.message
        }
    }

    public static async getFolders(
        accounts: Account | Account[] | null = null
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: MailboxController._get_accounts(accounts)
                },
            },
        );

        if (response.success && response.data) {
            const standardFolderList = Object.values(Folder).map(
                (folder) => folder.trim() + ":",
            );

            // Extract standard and custom folders from data
            response.data.forEach((account) => {
                // Standard folders
                let standardFolders = SharedStore.standardFolders.find(
                    item => item.email_address === account.email_address
                )

                if (!standardFolders) {
                    SharedStore.standardFolders = [
                        {
                            "email_address": account.email_address,
                            "result": []
                        }
                    ];
                    standardFolders = SharedStore.standardFolders[0];
                }

                standardFolderList.forEach((standardFolder) => {
                    const matchedFolder = account.result.find((folder) =>
                        folder
                            .trim()
                            .startsWith(standardFolder),
                    );
                    if (matchedFolder) {
                        standardFolders.result.push(matchedFolder);
                    }
                });

                // Custom folders
                let customFolders = SharedStore.customFolders.find(
                    item => item.email_address === account.email_address
                );

                if (!customFolders) {
                    SharedStore.customFolders = [
                        {
                            "email_address": account.email_address,
                            "result": []
                        }
                    ];
                    customFolders = SharedStore.customFolders[0];
                }

                customFolders.result = account.result.filter(
                    (folder) => {
                        return (
                            standardFolders.result.includes(
                                folder,
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

    public static async getMailboxes(
        accounts: Account | Account[] | null = null,
        folder: Folder | string | undefined = undefined,
        searchCriteria: SearchCriteria | string | undefined = undefined,
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: MailboxController._get_accounts(accounts),
                },
                queryParams: {
                    folder: folder,
                    search:
                        searchCriteria && typeof searchCriteria !== "string"
                            ? JSON.stringify(searchCriteria)
                            : searchCriteria,
                },
            },
        );

        if (response.success && response.data) {
            if (accounts && SharedStore.mailboxes.length > 0) {
                response.data.forEach(account => {
                    const targetMailbox = SharedStore.mailboxes.find(current => current.email_address === account.email_address);
                    if (targetMailbox) {
                        targetMailbox.result = account.result;
                    }
                });
            } else {
                SharedStore.mailboxes = response.data;
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async paginateEmails(
        accounts: Account | Account[] | null = null,
        offset_start?: number,
        offset_end?: number
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: MailboxController._get_accounts(accounts),
                    offset_start: offset_start,
                    offset_end: offset_end,
                },
            },
        );

        if (response.success && response.data) {
            response.data.forEach(account => {
                const targetMailbox = SharedStore.mailboxes.find(current => current.email_address === account.email_address);
                if (targetMailbox) {
                    targetMailbox.result = account.result;
                }
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async getEmailContent(
        account: Account,
        folder: string,
        uid: string,
    ): Promise<GetResponse<GetRoutes.GET_EMAIL_CONTENT>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_EMAIL_CONTENT,
            {
                pathParams: {
                    account: MailboxController._get_accounts(account),
                    folder: folder,
                    uid: uid,
                },
            },
        );
    }

    public static async downloadAttachment(
        account: Account,
        folder: string,
        uid: string,
        name: string,
        cid: string | undefined = undefined
    ): Promise<GetResponse<GetRoutes.DOWNLOAD_ATTACHMENT>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.DOWNLOAD_ATTACHMENT,
            {
                pathParams: {
                    account: MailboxController._get_accounts(account),
                    folder: folder,
                    uid: uid,
                    name: name
                },
                queryParams: {
                    cid: cid
                }
            },
        );
    }

    public static async sendEmail(formData: FormData): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.SEND_EMAIL,
            formData,
        );
    }

    public static async replyEmail(formData: FormData, original_message_id: string): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.REPLY_EMAIL,
            formData,
            {
                pathParams: {
                    original_message_id
                }
            }
        );
    }

    public static async forwardEmail(formData: FormData, original_message_id: string): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.FORWARD_EMAIL,
            formData,
            {
                pathParams: {
                    original_message_id
                }
            }
        );
    }

    public static async deleteEmails(
        account: Account,
        selection: string[],
        folder: string
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: folder,
            },
        );

        if (response.success) {
            MailboxController.getMailboxes(account);
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async moveEmails(
        account: Account,
        selection: string[],
        sourceFolder: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                source_folder: sourceFolder,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            MailboxController.getMailboxes(account);
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async copyEmails(
        account: Account,
        selection: string[],
        sourceFolder: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.COPY_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                source_folder: sourceFolder,
                destination_folder: destinationFolder,
            },
        );

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async markEmails(
        account: Account,
        selection: string[],
        mark: string | Mark,
        folder: string
    ): Promise<BaseResponse> {
        selection = selection.map(uid => removeWhitespaces(uid));
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MARK_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                mark: mark,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: folder
            },
        );

        if (response.success) {
            const targetMailbox = SharedStore.mailboxes.find(item => item.email_address === account.email_address);
            if (targetMailbox) {
                targetMailbox.result.emails.forEach(
                    (email: Email) => {
                        if (
                            (selection.includes("*") || selection.includes(email.uid.trim())) &&
                            Object.hasOwn(email, "flags") &&
                            email.flags
                        ) {
                            email.flags.push(mark);
                        }
                    },
                );
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async unmarkEmails(
        account: Account,
        selection: string[],
        mark: string | Mark,
        folder: string
    ): Promise<BaseResponse> {
        selection = selection.map(uid => removeWhitespaces(uid));
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.UNMARK_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                mark: mark,
                sequence_set: selection.includes("*")
                    ? "1:*"
                    : selection.join(","),
                folder: folder
            },
        );

        if (response.success) {
            const targetMailbox = SharedStore.mailboxes.find(item => item.email_address === account.email_address);
            if (targetMailbox) {
                targetMailbox.result.emails.forEach(
                    (email: Email) => {
                        if (
                            (selection.includes("*") || selection.includes(email.uid.trim())) &&
                            Object.hasOwn(email, "flags") &&
                            email.flags
                        ) {
                            email.flags = email.flags.filter(
                                (flag: string) => flag !== mark,
                            );
                        }
                    },
                );
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async createFolder(
        account: Account,
        folderName: string,
        parentFolder: string | undefined,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.CREATE_FOLDER,
            {
                account: MailboxController._get_accounts(account),
                folder_name: folderName,
                parent_folder: parentFolder,
            },
        );

        if (response.success) {
            SharedStore.customFolders.forEach((item) => {
                if (item.email_address == account.email_address) {
                    item.result.push(
                        parentFolder ? `${parentFolder}/${folderName}` : folderName,
                    );
                }
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async moveFolder(
        account: Account,
        folderName: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_FOLDER,
            {
                account: MailboxController._get_accounts(account),
                folder_name: folderName,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            const customFolders = SharedStore.customFolders.find(item => item.email_address == account.email_address);
            if (customFolders) {
                customFolders.result = customFolders.result.filter((e) => e !== folderName);

                let newFolderPath = `${destinationFolder}/${folderName}`;
                if (folderName.includes("/")) {
                    const tempLastIndex = folderName.lastIndexOf("/");
                    const parentFolder = folderName.slice(0, tempLastIndex);
                    if (customFolders.result.includes(parentFolder)) {
                        newFolderPath = `${destinationFolder}/${folderName.slice(tempLastIndex + 1)}`;
                    }
                }
                customFolders.result.push(newFolderPath);
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async renameFolder(
        account: Account,
        folderPath: string,
        newFolderName: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RENAME_FOLDER,
            {
                account: MailboxController._get_accounts(account),
                folder_name: folderPath,
                new_folder_name: newFolderName,
            },
        );

        if (response.success) {
            SharedStore.customFolders.forEach((item) => {
                if (item.email_address == account.email_address) {
                    item.result = item.result.map((folderName) => {
                        return folderName.replace(
                            folderPath.includes("/")
                                ? folderPath.slice(folderPath.lastIndexOf("/") + 1)
                                : folderPath,
                            newFolderName,
                        );
                    });
                }
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async deleteFolder(
        account: Account,
        folderName: string,
        subfolders: boolean,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_FOLDER,
            {
                account: MailboxController._get_accounts(account),
                folder_name: folderName,
                subfolders: subfolders,
            },
        );

        if (response.success) {
            SharedStore.customFolders.forEach((item) => {
                if (item.email_address == account.email_address) {
                    item.result = item.result.filter(
                        (e) =>
                            (e !== folderName && !subfolders) ||
                            !e.includes(folderName),
                    );
                }
            });
        }

        return {
            success: response.success,
            message: response.message,
        };
    }
}
