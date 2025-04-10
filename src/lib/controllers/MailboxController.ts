import { SharedStore } from "$lib/stores/shared.svelte";
import {
    ApiService,
    GetRoutes,
    type BaseResponse,
    type GetResponse,
    PostRoutes,
    type PostResponse,
} from "$lib/services/ApiService";
import { MAILBOX_LENGTH, PAGINATE_MAILBOX_CHECK_DELAY_MS, WAIT_FOR_EMAILS_TIMEOUT } from "$lib/constants";
import {
    Folder,
    Mark,
    type Account,
    type Draft,
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
    roundUpToMultiple,
} from "$lib/utils";

export class MailboxController {
    public static async init(failedOnly: boolean = false): Promise<BaseResponse> {
        let response = {
            success: false,
            message: "Initialize does not finished.",
        };

        const folderResults = await Promise.allSettled(
            (failedOnly ? SharedStore.failedFolders : SharedStore.accounts).map(async (account) => {
                return {
                    account: account,
                    response: await MailboxController.getFolders(account)
                }
            }),
        );

        folderResults.forEach((result) => {
            if (result.status === "fulfilled") {
                response.success = result.value.response.success;
                response.message = result.value.response.message;
                if (!response.success) {
                    SharedStore.failedFolders.push(result.value.account);
                }
            } else {
                response.success = false;
                response.message = "Error while initializing folders.";
            }
        });

        const mailboxResults = await Promise.allSettled(
            (failedOnly ? SharedStore.failedMailboxes : SharedStore.accounts).map(async (account) => {
                return {
                    account: account,
                    response: await MailboxController.getMailbox(
                        account,
                        Folder.Inbox,
                        { excluded_flags: [Mark.Seen] }
                    )
                }
            })
        );

        mailboxResults.forEach((result) => {
            if (result.status === "fulfilled") {
                response.success = result.value.response.success;
                response.message = result.value.response.message;
                if (!response.success) {
                    SharedStore.failedMailboxes.push(result.value.account);
                }
            } else {
                response.success = false;
                response.message = "Error while initializing mailboxes.";
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
            SharedStore.mailboxes[account.email_address] = {
                total: response.data[account.email_address].total,
                emails: {
                    prev: [],
                    current: response.data[account.email_address].emails,
                    next: [],
                },
                folder: response.data[account.email_address].folder,
            };

            if (offsetStart > 1) {
                MailboxController.paginateEmails(
                    account,
                    offsetStart - 1 - MAILBOX_LENGTH,
                    offsetStart - 1,
                );
            }

            if (
                offsetEnd < SharedStore.mailboxes[account.email_address].total
            ) {
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
            const mailbox = response.data[account.email_address];
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
        if (Object.hasOwn(SharedStore.recentEmails, account.email_address)) {
            SharedStore.recentEmails[account.email_address] =
                SharedStore.recentEmails[account.email_address].filter(
                    (email) => email.uid !== uid,
                );
        }
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

    public static async sendEmail(
        email: FormData | Draft,
    ): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.SEND_EMAIL,
            email,
        );
    }

    public static async replyEmail(
        originalMessageId: string,
        email: FormData | Draft,
    ): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.REPLY_EMAIL,
            email,
            {
                pathParams: {
                    original_message_id: originalMessageId,
                },
            },
        );
    }

    public static async forwardEmail(
        originalMessageId: string,
        email: FormData | Draft,
    ): Promise<PostResponse> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.FORWARD_EMAIL,
            email,
            {
                pathParams: {
                    original_message_id: originalMessageId,
                },
            },
        );
    }

    public static async saveEmailAsDraft(
        email: FormData | Draft,
        appenduid?: string,
    ): Promise<PostResponse<PostRoutes.SAVE_EMAIL_AS_DRAFT>> {
        return await ApiService.post(
            SharedStore.server,
            PostRoutes.SAVE_EMAIL_AS_DRAFT,
            {
                email,
                appenduid,
            },
        );
    }

    public static async deleteEmails(
        account: Account,
        selection: string,
        folder: string,
        offset?: number,
    ): Promise<PostResponse> {
        const response = await ApiService.post(
            SharedStore.server,
            PostRoutes.DELETE_EMAIL,
            {
                account: account.email_address,
                sequence_set: removeWhitespaces(selection),
                folder: folder,
            },
        );

        if (!response.success) return response;

        const currentMailbox = SharedStore.mailboxes[account.email_address];

        if (!isExactFolderMatch(currentMailbox.folder, folder)) return response;

        // selection will be either 1:* or uids separated with comma
        // something like 1,2,3,4 but not 2:* or 1,3:*:5
        if (selection === "1:*") {
            currentMailbox.emails = { prev: [], current: [], next: [] };
            currentMailbox.total = 0;
            return response;
        }

        // Delete emails from current mailbox and update total count.
        const countBeforeDelete = currentMailbox.emails.current.length;
        const wasFullBeforeDelete = countBeforeDelete >= MAILBOX_LENGTH;
        currentMailbox.emails.current = currentMailbox.emails.current.filter(
            (email) =>
                !isUidInSelection(selection, removeWhitespaces(email.uid)),
        );
        const deletedCount =
            countBeforeDelete - currentMailbox.emails.current.length;
        currentMailbox.total -= deletedCount;

        // If the offset is not given, we can't determine how
        // deleted emails should be replaced.
        // Also, if the `current` page wasn't full before deletion,
        // there may be no emails available to replace the deleted ones.
        if (!offset || !wasFullBeforeDelete) return response;

        // If we have reached the end of the mailbox then again
        // there can't be any email to replace deleted ones.
        const offsetEnd = roundUpToMultiple(offset, MAILBOX_LENGTH);
        if (currentMailbox.total <= offsetEnd) return response;

        // After the selected emails are removed from current,
        // add back to `current` from `next` as many emails as were removed
        // (if not available, they should be loading, so wait for them;
        // if they are not loading, there is a problem because
        // when the number of emails in `next` decreases, new emails
        // should be loaded to bring `next` back to MAILBOX_LENGTH
        // using `paginateEmails()`) and then fetch enough emails from the server
        // with the `paginateEmails()` to bring `next` back to `MAILBOX_LENGTH`.
        // For example: current mailbox displays emails from
        // 1 to 10 and user delete 5 of them. Since next contains
        // emails from 11 to 20 (as explained above), get
        // first 5 emails from next i.e. 11,12,13,14,15 and
        // add them to the current. This way, the current should
        // reach `MAILBOX_LENGTH`. Hovewer, since 11,12,13,14,15 were
        // deleted, fill the gap of 5 emails by fetching 21,22,23,24,25
        // with `paginateEmails()` function.
        const processNextBatch = () => {
            currentMailbox.emails.current.push(
                ...currentMailbox.emails.next.splice(0, deletedCount),
            );

            const nextOfNext = offsetEnd + MAILBOX_LENGTH + 1;
            if (currentMailbox.total >= nextOfNext + 1) {
                MailboxController.paginateEmails(
                    account,
                    nextOfNext,
                    nextOfNext + deletedCount - 1,
                );
            }
        };

        return new Promise((resolve) => {
            let waitNext: ReturnType<typeof setInterval> | null;

            const clearWaitNextInterval = () => {
                if (waitNext) {
                    clearInterval(waitNext)
                    waitNext = null;
                    resolve(response);
                }
            }

            if (currentMailbox.emails.next.length > 0) {
                processNextBatch();
                clearWaitNextInterval();
            } else {
                const startTime = Date.now();
                waitNext = setInterval(() => {
                    if (Date.now() - startTime >= WAIT_FOR_EMAILS_TIMEOUT) {
                        clearWaitNextInterval();
                    }
                    if (currentMailbox.emails.next.length > 0) {
                        processNextBatch();
                        clearWaitNextInterval();
                    }
                }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
            }
        });
    }

    public static async moveEmails(
        account: Account,
        selection: string,
        sourceFolder: string,
        destinationFolder: string,
        offset?: number,
    ): Promise<PostResponse> {
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

        if (!response.success) return response;

        // Continue with the same steps as deleteEmails from this point,
        // but only if the current folder matches the source folder.

        const currentMailbox = SharedStore.mailboxes[account.email_address];

        if (!isExactFolderMatch(currentMailbox.folder, sourceFolder)) return response;

        if (selection === "1:*") {
            currentMailbox.emails = { prev: [], current: [], next: [] };
            currentMailbox.total = 0;
            return response;
        }

        const countBeforeMove = currentMailbox.emails.current.length;
        const wasFullBeforeMove = countBeforeMove >= MAILBOX_LENGTH;
        currentMailbox.emails.current = currentMailbox.emails.current.filter(
            (email) =>
                !isUidInSelection(selection, removeWhitespaces(email.uid)),
        );
        const movedCount = countBeforeMove - currentMailbox.emails.current.length;
        currentMailbox.total -= movedCount;

        if (!offset || !wasFullBeforeMove) return response;

        const offsetEnd = roundUpToMultiple(offset, MAILBOX_LENGTH);
        if (currentMailbox.total <= offsetEnd) return response;

        const processNextBatch = () => {
            currentMailbox.emails.current.push(
                ...currentMailbox.emails.next.splice(0, movedCount),
            );

            const nextOfNext = offsetEnd + MAILBOX_LENGTH + 1;
            if (currentMailbox.total >= nextOfNext + 1) {
                MailboxController.paginateEmails(
                    account,
                    nextOfNext,
                    nextOfNext + movedCount - 1,
                );
            }
        };

        return new Promise((resolve) => {
            let waitNext: ReturnType<typeof setInterval> | null;

            const clearNextInterval = () => {
                if (waitNext) {
                    clearInterval(waitNext);
                    waitNext = null;
                    resolve(response);
                }
            }

            if (currentMailbox.emails.next.length > 0) {
                processNextBatch();
                clearNextInterval();
            } else {
                const startTime = Date.now();
                waitNext = setInterval(() => {
                    if (Date.now() - startTime >= WAIT_FOR_EMAILS_TIMEOUT) {
                        clearNextInterval();
                    }
                    if (currentMailbox.emails.next.length > 0) {
                        processNextBatch();
                        clearNextInterval();
                    }
                }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
            }
        });
    }

    public static async copyEmails(
        account: Account,
        selection: string,
        sourceFolder: string,
        destinationFolder: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async markEmails(
        account: Account,
        selection: string,
        mark: string | Mark,
        folder: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async unmarkEmails(
        account: Account,
        selection: string,
        mark: string | Mark,
        folder: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async createFolder(
        account: Account,
        folderName: string,
        parentFolder?: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async moveFolder(
        account: Account,
        folderName: string,
        destinationFolder: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async renameFolder(
        account: Account,
        folderName: string,
        newFolderName: string,
    ): Promise<PostResponse> {
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

        return response;
    }

    public static async deleteFolder(
        account: Account,
        folderName: string,
        delete_subfolders: boolean,
    ): Promise<PostResponse> {
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

        return response;
    }
}
