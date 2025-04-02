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
import {
    extractFolderName,
    isExactFolderMatch,
    isStandardFolder,
    isSubfolderOrMatch,
    isUidInSelection,
    removeFromPath,
    removeWhitespaces,
    replaceFolderName,
} from "$lib/utils";

export const MAILBOX_LENGTH = 10;

export class MailboxController {
    public static async init(): Promise<BaseResponse> {
        let response = {
            success: false,
            message: "Initialize does not finished.",
        };

        const folderResults = await Promise.allSettled(
            SharedStore.accounts.map((account) =>
                MailboxController.getFolders(account),
            ),
        );

        folderResults.forEach((result) => {
            if (result.status === "fulfilled") {
                response.success = result.value.success;
                response.message = result.value.message;
                if (!result.value.success) {
                    // TODO: push result.value.something into failedFolders
                }
            } else {
                response.success = false;
                response.message = "Error while initializing folders.";
                // TODO: push result.reason.something into failedFolders
            }
        });

        const mailboxResults = await Promise.allSettled(
            SharedStore.accounts.map((account) =>
                MailboxController.getMailbox(account, Folder.Inbox, {
                    excluded_flags: [Mark.Seen],
                }),
            ),
        );

        mailboxResults.forEach((result) => {
            if (result.status === "fulfilled") {
                response.success = result.value.success;
                response.message = result.value.message;
                if (!result.value.success) {
                    // TODO: push result.value.something into failedFolders
                }
            } else {
                response.success = false;
                response.message = "Error while initializing mailboxes.";
                // TODO: push result.reason.something into failedFolders
            }
        });

        return {
            success: response.success,
            message: response.success
                ? "Mailbox Controller Initialized"
                : response.message,
        };
    }

    public static async getFolders(account: Account): Promise<BaseResponse> {
        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_FOLDERS,
            {
                pathParams: {
                    accounts: account.email_address,
                },
            },
        );

        if (response.success && response.data) {
            // Extract standard and custom folders from data
            // and add them to SharedStore
            for (const email_address in response.data) {
                let folders = SharedStore.folders[email_address];
                if (!folders) {
                    SharedStore.folders[email_address] = {
                        standard: [],
                        custom: [],
                    };
                }
                response.data[email_address].forEach((folder) => {
                    if (isStandardFolder(folder)) {
                        SharedStore.folders[email_address].standard.push(
                            folder,
                        );
                    } else {
                        SharedStore.folders[email_address].custom.push(folder);
                    }
                });
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async getMailbox(
        account: Account,
        folder?: Folder | string,
        searchCriteria?: SearchCriteria | string,
        offsetStart?: number,
        offsetEnd?: number,
    ): Promise<BaseResponse> {
        offsetStart = Math.max(1, offsetStart ?? 1);
        offsetEnd = Math.max(1, offsetEnd ?? offsetStart - 1 + MAILBOX_LENGTH);

        if (offsetStart > offsetEnd) {
            throw Error("`offsetStart` can not be larger than `offsetEnd`");
        }

        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOX,
            {
                pathParams: {
                    account: account.email_address,
                },
                queryParams: {
                    folder: folder,
                    search:
                        searchCriteria && typeof searchCriteria !== "string"
                            ? JSON.stringify(searchCriteria)
                            : searchCriteria,
                    offset_start: offsetStart,
                    offset_end: offsetEnd,
                },
            },
        );

        if (response.success && response.data) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];
            const mailboxes =
                Object.keys(SharedStore.mailboxes).length > 0
                    ? Object.values(response.data)
                    : [response.data[account.email_address]];

            mailboxes.forEach((mailbox) => {
                currentMailbox.total = mailbox.total;
                currentMailbox.folder = mailbox.folder;
                currentMailbox.emails = {
                    prev: [],
                    current: mailbox.emails,
                    next: [],
                };
            });

            if (offsetStart > 1) {
                MailboxController.paginateEmails(
                    account,
                    offsetStart - 1 - MAILBOX_LENGTH,
                    offsetStart - 1,
                );
            }

            if (currentMailbox.total > offsetEnd) {
                MailboxController.paginateEmails(
                    account,
                    offsetEnd + 1,
                    offsetEnd + 1 + MAILBOX_LENGTH,
                );
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async paginateEmails(
        account: Account,
        offsetStart?: number,
        offsetEnd?: number,
    ): Promise<BaseResponse> {
        const currentMailbox = SharedStore.mailboxes[account.email_address];

        offsetStart = Math.min(
            currentMailbox.total,
            Math.max(1, offsetStart ?? 1),
        );
        offsetEnd = Math.min(
            currentMailbox.total,
            Math.max(1, offsetEnd ?? offsetStart - 1 + MAILBOX_LENGTH),
        );

        if (offsetStart > offsetEnd) {
            throw Error("`offsetStart` can not be larger than `offsetEnd`");
        }

        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.PAGINATE_MAILBOX,
            {
                pathParams: {
                    account: account.email_address,
                    offset_start: offsetStart,
                    offset_end: offsetEnd,
                },
            },
        );

        if (response.success && response.data) {
            const currentEmails = currentMailbox.emails.current;
            const [, mailbox] = Object.values(response.data);
            if (
                Number(mailbox.emails[0].uid) <=
                Number(currentEmails[currentEmails.length - 1].uid)
            ) {
                currentMailbox.emails.next = mailbox.emails;
            } else {
                currentMailbox.emails.prev = mailbox.emails;
            }
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
                    account: account.email_address,
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
                    account: account.email_address,
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
        originalMessageId: string,
        formData: FormData,
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
        originalMessageId: string,
        formData: FormData,
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
        offsetEndBeforeDelete?: number,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: account.email_address,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];

            // selection will be either 1:* or uids separated with comma
            // something like 1,2,3,4 but not 2:* or 1,3:*:5
            if (isExactFolderMatch(currentMailbox.folder, folder)) {
                if (selection === "1:*") {
                    currentMailbox.emails.current = [];

                    if (offsetEndBeforeDelete) {
                        // After the selected emails are removed from current,
                        // add back to current from next as many emails as were removed
                        // (if not available, they should be loading, so wait for them;
                        // if they are not loading, there is a problem because
                        // when the number of emails in next decreases, new emails
                        // should be loaded to bring next back to MAILBOX_LENGTH
                        // using `paginateEmails()`) and then fetch enough emails from the server
                        // with the `paginateEmails()` to bring next back to `MAILBOX_LENGTH`.
                        const waitNext = setInterval(() => {
                            if (currentMailbox.emails.next.length > 0) {
                                currentMailbox.emails.current = currentMailbox.emails.next;
                                clearInterval(waitNext);
                                MailboxController.paginateEmails(
                                    account,
                                    offsetEndBeforeDelete * 2 + 1,
                                );
                            }
                        }, 100);
                    }
                } else {
                    const countBeforeDelete = currentMailbox.emails.current.length;
                    currentMailbox.emails.current =
                        currentMailbox.emails.current.filter(
                            (email) =>
                                !isUidInSelection(
                                    selection,
                                    removeWhitespaces(email.uid),
                                ),
                        );

                    if (offsetEndBeforeDelete) {
                        // Same as above, but part of the current not whole.
                        // For example: current mailbox displays emails from
                        // 1 to 10 and user delete 5 of them. Since next contains
                        // emails from 11 to 20 (as explained above), get
                        // first 5 emails from next i.e. 11,12,13,14,15 and
                        // add them to the current. This way, the current should
                        // reach `MAILBOX_LENGTH`. Hovewer, since 11,12,13,14,15 were
                        // deleted, fill the gap of 5 emails by fetching 21,22,23,24,25
                        // with `paginateEmails()` function.
                        const waitNext = setInterval(() => {
                            if (currentMailbox.emails.next.length > 0) {
                                const deletedCount = countBeforeDelete - currentMailbox.emails.current.length;
                                currentMailbox.emails.current.push(
                                    ...currentMailbox.emails.next.splice(
                                        0,
                                        deletedCount,
                                    ),
                                );
                                clearInterval(waitNext);
                                MailboxController.paginateEmails(
                                    account,
                                    offsetEndBeforeDelete * 2 + 1,
                                    offsetEndBeforeDelete * 2 + deletedCount,
                                );
                            }
                        }, 100);
                    }
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
        offsetEndBeforeMove?: number
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.MOVE_EMAIL,
            {
                account: account.email_address,
                sequence_set: removeWhitespaces(selection),
                source_folder: sourceFolder,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            // same as `deleteEmails()`
            const currentMailbox = SharedStore.mailboxes[account.email_address];
            if (isExactFolderMatch(currentMailbox.folder, sourceFolder)) {
                if (selection === "1:*") {
                    currentMailbox.emails.current = [];

                    if (offsetEndBeforeMove) {
                        const waitNext = setInterval(() => {
                            if (currentMailbox.emails.next.length > 0) {
                                currentMailbox.emails.current = currentMailbox.emails.next;
                                clearInterval(waitNext);
                                MailboxController.paginateEmails(
                                    account,
                                    offsetEndBeforeMove * 2 + 1,
                                );
                            }
                        }, 100);
                    }
                } else {
                    const countBeforeMove = currentMailbox.emails.current.length;
                    currentMailbox.emails.current =
                        currentMailbox.emails.current.filter(
                            (email) =>
                                !isUidInSelection(
                                    selection,
                                    removeWhitespaces(email.uid),
                                ),
                        );

                    if (offsetEndBeforeMove) {
                        const waitNext = setInterval(() => {
                            if (currentMailbox.emails.next.length > 0) {
                                const deletedCount = countBeforeMove - currentMailbox.emails.current.length;
                                currentMailbox.emails.current.push(
                                    ...currentMailbox.emails.next.splice(
                                        0,
                                        deletedCount,
                                    ),
                                );
                                clearInterval(waitNext);
                                MailboxController.paginateEmails(
                                    account,
                                    offsetEndBeforeMove * 2 + 1,
                                    offsetEndBeforeMove * 2 + deletedCount,
                                );
                            }
                        }, 100);
                    }
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
                account: account.email_address,
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
                account: account.email_address,
                mark: mark,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];
            currentMailbox.emails.current.forEach((email: Email) => {
                if (
                    Object.hasOwn(email, "flags") &&
                    email.flags &&
                    (selection === "1:*" ||
                        isUidInSelection(
                            selection,
                            removeWhitespaces(email.uid),
                        ))
                ) {
                    email.flags.push(mark);
                }
            });
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
                account: account.email_address,
                mark: mark,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];
            currentMailbox.emails.current.forEach((email: Email) => {
                if (
                    Object.hasOwn(email, "flags") &&
                    email.flags &&
                    (selection === "1:*" ||
                        isUidInSelection(
                            selection,
                            removeWhitespaces(email.uid),
                        ))
                ) {
                    email.flags = email.flags.filter(
                        (flag: string) => flag !== mark,
                    );
                }
            });
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
                account: account.email_address,
                folder_name: folderName,
                parent_folder: parentFolder,
            },
        );

        if (response.success) {
            SharedStore.folders[account.email_address].custom.push(
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
                account: account.email_address,
                folder_name: folderName,
                destination_folder: destinationFolder,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];

            const oldFolderName = extractFolderName(folderName);
            if (destinationFolder !== "") destinationFolder += "/";
            const newFolderPath = `${destinationFolder}${folderName}`;

            SharedStore.folders[account.email_address].custom.map(
                (customFolderPath) => {
                    if (isSubfolderOrMatch(customFolderPath, oldFolderName)) {
                        return replaceFolderName(
                            customFolderPath,
                            oldFolderName,
                            newFolderPath,
                        );
                    }
                },
            );

            if (isSubfolderOrMatch(currentMailbox.folder, oldFolderName)) {
                currentMailbox.folder = replaceFolderName(
                    currentMailbox.folder,
                    oldFolderName,
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
        folderName: string,
        newFolderName: string,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.RENAME_FOLDER,
            {
                account: account.email_address,
                folder_name: folderName,
                new_folder_name: newFolderName,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];

            const oldFolderName = extractFolderName(folderName);

            SharedStore.folders[account.email_address].custom.map(
                (customFolder) => {
                    return replaceFolderName(
                        customFolder,
                        oldFolderName,
                        newFolderName,
                    );
                },
            );

            if (isSubfolderOrMatch(currentMailbox.folder, oldFolderName)) {
                currentMailbox.folder = replaceFolderName(
                    currentMailbox.folder,
                    oldFolderName,
                    newFolderName,
                );
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }

    public static async deleteFolder(
        account: Account,
        folderName: string,
        delete_subfolders: boolean,
    ): Promise<BaseResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_FOLDER,
            {
                account: account.email_address,
                folder_name: folderName,
                delete_subfolders: delete_subfolders,
            },
        );

        if (response.success) {
            const currentMailbox = SharedStore.mailboxes[account.email_address];
            const currentFolders = SharedStore.folders[account.email_address];
            currentFolders.custom = currentFolders.custom.filter(
                (customFolderPath) => {
                    if (isExactFolderMatch(customFolderPath, folderName)) {
                        return false;
                    } else if (
                        isSubfolderOrMatch(customFolderPath, folderName)
                    ) {
                        return !delete_subfolders;
                    }
                },
            );

            if (isExactFolderMatch(currentMailbox.folder, folderName)) {
                SharedStore.mailboxes[account.email_address] = {
                    folder: "",
                    emails: { prev: [], current: [], next: [] },
                    total: 0,
                };
            } else if (isSubfolderOrMatch(currentMailbox.folder, folderName)) {
                currentMailbox.folder = removeFromPath(
                    currentMailbox.folder,
                    folderName,
                );
            }
        }

        return {
            success: response.success,
            message: response.message,
        };
    }
}
