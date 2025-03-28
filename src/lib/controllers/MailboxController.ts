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
import { MAILBOX_LENGTH } from "$lib/constants";

export class MailboxController {
    private static _get_accounts(
        accounts: Account | Account[] | string[] | null = null,
    ): string {
        if (accounts && !Array.isArray(accounts)) {
            accounts = [accounts];
        }

        return (
            accounts && accounts.length > 0 ? accounts : SharedStore.accounts
        )
            .map((account) => {
                return typeof account !== "string"
                    ? account.email_address
                    : account;
            })
            .join(",");
    }

    public static async init(): Promise<BaseResponse> {
        let response;
        response = await MailboxController.getFolders();
        if (!response.success) {
            return {
                success: response.success,
                message: response.message,
            };
        }

        response = await MailboxController.getMailboxes(
            SharedStore.accounts,
            Folder.Inbox,
            {
                excluded_flags: [Mark.Seen],
            },
        );
        return {
            success: response.success,
            message: response.success
                ? "Mailbox Controller Initialized"
                : response.message,
        };
    }

    public static async getFolders(
        accounts: Account | Account[] | null = null,
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: MailboxController._get_accounts(accounts),
                },
            },
        );

        if (response.success && response.data) {
            const standardFolderList = Object.values(Folder).map(
                (folder) => folder.trim() + ":",
            );

            // Extract standard and custom folders from data
            // and add them to SharedStore
            for (const email_address in response.data) {
                let standardFolders =
                    SharedStore.standardFolders[email_address];
                if (!standardFolders) {
                    SharedStore.standardFolders[email_address] = [];
                }

                SharedStore.standardFolders[email_address] = response.data[
                    email_address
                ].filter((folder) => {
                    const isStandardFolder = standardFolderList.some(
                        (standardFolder) =>
                            folder.trim().startsWith(standardFolder),
                    );
                    if (isStandardFolder) {
                        SharedStore.standardFolders[email_address].push(folder);
                    } else {
                        SharedStore.customFolders[email_address].push(folder);
                    }
                });
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async getMailboxes(
        accounts: Account | Account[] | null = null,
        folder?: Folder | string,
        searchCriteria?: SearchCriteria | string,
        offsetStart?: number,
        offsetEnd?: number,
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
                    offset_start: Math.max(1, offsetStart ?? 1),
                    offset_end: Math.max(1, offsetEnd ?? MAILBOX_LENGTH),
                },
            },
        );

        if (response.success && response.data) {
            if (accounts && SharedStore.mailboxes.length > 0) {
                response.data.forEach((account) => {
                    const targetMailbox = SharedStore.mailboxes.find(
                        (current) =>
                            current.email_address === account.email_address,
                    );
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
        offsetStart?: number,
        offsetEnd?: number,
    ): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOXES,
            {
                pathParams: {
                    accounts: MailboxController._get_accounts(accounts),
                    offset_start: Math.max(1, offsetStart ?? 1),
                    offset_end: Math.max(1, offsetEnd ?? MAILBOX_LENGTH),
                },
            },
        );

        if (response.success && response.data) {
            response.data.forEach((account) => {
                const targetMailbox = SharedStore.mailboxes.find(
                    (current) =>
                        current.email_address === account.email_address,
                );
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
        cid?: string,
    ): Promise<GetResponse<GetRoutes.DOWNLOAD_ATTACHMENT>> {
        return await ApiService.get(
            SharedStore.server,
            GetRoutes.DOWNLOAD_ATTACHMENT,
            {
                pathParams: {
                    account: MailboxController._get_accounts(account),
                    folder: folder,
                    uid: uid,
                    name: name,
                },
                queryParams: {
                    cid: cid,
                },
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

    public static async replyEmail(
        formData: FormData,
        originalMessageId: string,
    ): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.REPLY_EMAIL,
            formData,
            {
                pathParams: {
                    original_message_id: originalMessageId,
                },
            },
        );
    }

    public static async forwardEmail(
        formData: FormData,
        originalMessageId: string,
    ): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.FORWARD_EMAIL,
            formData,
            {
                pathParams: {
                    original_message_id: originalMessageId,
                },
            },
        );
    }

    public static async deleteEmails(
        account: Account,
        selection: string,
        folder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            // selection will be either 1:* or uids separated with comma
            // something like 1,2,3,4 but not 2:* or 1,3:*:5
            if (
                SharedStore.mailboxes[account.email_address].folder ===
                folder
            ) {
                if (selection !== "1:*") {
                    SharedStore.mailboxes[
                        account.email_address
                    ].emails.current = SharedStore.mailboxes[
                        account.email_address
                    ].emails.current.filter(
                        (email) =>
                            !selection.includes(removeWhitespaces(email.uid)),
                    );
                } else {
                    SharedStore.mailboxes[
                        account.email_address
                    ].emails.current = [];
                }
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async moveEmails(
        account: Account,
        selection: string,
        sourceFolder: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: removeWhitespaces(selection),
                source_folder: sourceFolder,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            // selection will be either 1:* or uids separated with comma
            // something like 1,2,3,4 but not 2:* or 1,3:*:5
            if (
                SharedStore.mailboxes[account.email_address].folder ===
                sourceFolder
            ) {
                if (selection !== "1:*") {
                    SharedStore.mailboxes[
                        account.email_address
                    ].emails.current = SharedStore.mailboxes[
                        account.email_address
                    ].emails.current.filter(
                        (email) =>
                            !selection.includes(removeWhitespaces(email.uid)),
                    );
                } else {
                    SharedStore.mailboxes[
                        account.email_address
                    ].emails.current = [];
                }
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async copyEmails(
        account: Account,
        selection: string,
        sourceFolder: string,
        destinationFolder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.COPY_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                sequence_set: removeWhitespaces(selection),
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
        selection: string,
        mark: string | Mark,
        folder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MARK_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                mark: mark,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            SharedStore.mailboxes[account.email_address].emails.current.forEach(
                (email: Email) => {
                    if (
                        (selection === "1:*" ||
                            selection.includes(removeWhitespaces(email.uid))) &&
                        Object.hasOwn(email, "flags") &&
                        email.flags
                    ) {
                        email.flags.push(mark);
                    }
                },
            );
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async unmarkEmails(
        account: Account,
        selection: string,
        mark: string | Mark,
        folder: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.UNMARK_EMAIL,
            {
                account: MailboxController._get_accounts(account),
                mark: mark,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            SharedStore.mailboxes[account.email_address].emails.current.forEach(
                (email: Email) => {
                    if (
                        Object.hasOwn(email, "flags") &&
                        email.flags &&
                        (selection === "1:*" ||
                            selection.includes(removeWhitespaces(email.uid)))
                    ) {
                        email.flags = email.flags.filter(
                            (flag: string) => flag !== mark,
                        );
                    }
                },
            );
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async createFolder(
        account: Account,
        folderName: string,
        parentFolder?: string,
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
            SharedStore.customFolders[account.email_address].push(
                parentFolder ? `${parentFolder}/${folderName}` : folderName,
            );
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
            SharedStore.customFolders[account.email_address] =
                SharedStore.customFolders[account.email_address].filter(
                    (customFolder) => customFolder !== folderName,
                );

            let newFolderPath = `${destinationFolder}/${folderName}`;
            if (folderName.includes("/")) {
                const tempLastIndex = folderName.lastIndexOf("/");
                const parentFolder = folderName.slice(0, tempLastIndex);
                if (
                    SharedStore.customFolders[account.email_address].includes(
                        parentFolder,
                    )
                ) {
                    newFolderPath = `${destinationFolder}/${folderName.slice(tempLastIndex + 1)}`;
                }
                SharedStore.customFolders[account.email_address].push(
                    newFolderPath,
                );
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
            SharedStore.customFolders[account.email_address].map(
                (customFolder) => {
                    return customFolder.replace(
                        folderPath.includes("/")
                            ? folderPath.slice(folderPath.lastIndexOf("/") + 1)
                            : folderPath,
                        newFolderName,
                    );
                },
            );
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
            SharedStore.customFolders[account.email_address] =
                SharedStore.customFolders[account.email_address].filter(
                    (customFolder) =>
                        (customFolder !== folderName && !subfolders) ||
                        !customFolder.includes(folderName),
                );
        }

        return {
            success: response.success,
            message: response.message,
        };
    }
}
