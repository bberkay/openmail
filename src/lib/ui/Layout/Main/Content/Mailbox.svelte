<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Mailbox, Folder } from "$lib/types";
    import {
        PAGINATE_MAILBOX_CHECK_DELAY_MS,
        WAIT_FOR_EMAILS_TIMEOUT_MS,
    } from "$lib/constants";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { sortSelection } from "$lib/utils";

    /**
     * Initialize current mailbox listener.
     */
    let currentMailbox = $derived.by(() => {
        if (SharedStore.currentAccount === "home") {
            let currentMailbox: Mailbox = {
                total: 0,
                emails: { prev: [], current: [], next: [] },
                folder: Folder.Inbox, // mailboxes are going to be INBOX while selecting account to "home"
            };
            Object.values(SharedStore.mailboxes).forEach((mailbox) => {
                currentMailbox.total += mailbox.total;
                currentMailbox.emails.prev.push(...mailbox.emails.prev);
                currentMailbox.emails.current.push(...mailbox.emails.current);
                currentMailbox.emails.next.push(...mailbox.emails.next);
            });
            Object.values(currentMailbox.emails).forEach((emails) => {
                emails.sort(
                    (a, b) =>
                        new Date(b.date).getTime() - new Date(a.date).getTime(),
                );
            });
            return currentMailbox;
        } else {
            return SharedStore.mailboxes[
                SharedStore.currentAccount.email_address
            ];
        }
    });

    export function getCurrentMailbox() {
        return currentMailbox;
    }

    /**
     * MailboxContext Initializing
     */

    // Example of EmailSelection:
    // ["someone1@mail.com,2", "someone1@mail.com,3", "someone1@mail.com,6"]
    export type EmailSelection = "1:*" | string[];

    // Example of GroupedUidSelection:
    // [["someone1@mail.com", "2,3,6"], ["someone1@mail.com", "1,4,6"]]
    export type GroupedUidSelection = [email_address: string, uids: string][];

    // Example of GroupedMessageIdSelection:
    // [["someone1@mail.com", ["<1A0..>","<4C7..>"]], ["someone1@mail.com", ["<2QX..>","<39A..>"]]]
    export type GroupedMessageIdSelection = [
        email_address: string,
        message_ids: string[],
    ][];

    export const CONTEXT_KEY = "MAILBOX";
    export interface MailboxContext {
        currentOffset: { value: number };
        emailSelection: { value: EmailSelection };
        getGroupedUidSelection: () => GroupedUidSelection;
    }

    let currentOffset: { value: number } = $state({ value: 1 });
    let emailSelection: { value: EmailSelection } = $state({ value: [] });
    let groupedUidSelection: GroupedUidSelection = $derived.by(() => {
        if (!emailSelection) return [];

        const accountUidMap: Record<string, string> = {};
        // When `emailSelection` have become something like this:
        // ["account1@mail.com,123", "account1@mail.com,124", "account2@mail.com,123"]
        // `groupedUidSelection` will be something like this:
        // [["account1@mail.com", "123,124"], ["account2@mail.com", "123"]]
        // and with this way, we are minimizing api calls from this:
        // C: A101 +STORE FLAG account1@mail.com 123
        // C: A102 +STORE FLAG account1@mail.com 124
        // C: A103 +STORE FLAG account1@mail.com 125
        // to this:
        // C: A101 +STORE FLAG account1@mail.com 123, 124
        // C: A102 +STORE FLAG account1@mail.com 125
        if (emailSelection.value === "1:*") {
            if (SharedStore.currentAccount === "home") {
                SharedStore.accounts.forEach((account) => {
                    accountUidMap[account.email_address] = "1:*";
                });
            } else {
                accountUidMap[SharedStore.currentAccount.email_address] = "1:*";
            }
        } else {
            emailSelection.value.forEach((selection) => {
                const [emailAddr, uid] = selection.split(",");
                accountUidMap[emailAddr] = Object.hasOwn(
                    accountUidMap,
                    emailAddr,
                )
                    ? sortSelection(accountUidMap[emailAddr].concat(",", uid))
                    : uid;
            });
        }
        return Object.entries(accountUidMap);
    });

    /**
     * Mailbox filling logic.
     */

    let waitPrev: ReturnType<typeof setInterval> | null;

    export async function paginateMailboxBackward(
        currentOffset: number,
    ): Promise<void> {
        const MAILBOX_LENGTH = Number(SharedStore.preferences.mailboxLength);
        if (currentOffset <= MAILBOX_LENGTH) return;

        return new Promise((resolve) => {
            if (!waitPrev) {
                const emailAddrs =
                    SharedStore.currentAccount !== "home"
                        ? [SharedStore.currentAccount.email_address]
                        : SharedStore.accounts.map((acc) => acc.email_address);

                const shiftEmailPagesBackward = () => {
                    currentMailbox.emails.next = currentMailbox.emails.current;
                    currentMailbox.emails.current = currentMailbox.emails.prev;
                    currentMailbox.emails.prev = [];

                    const prevOffsetStart = Math.max(
                        1,
                        currentOffset - MAILBOX_LENGTH * 2,
                    );
                    const prevOffsetEnd = Math.max(
                        MAILBOX_LENGTH,
                        currentOffset - 1 - MAILBOX_LENGTH,
                    );

                    if (prevOffsetEnd < currentOffset) {
                        emailAddrs.forEach((emailAddr) => {
                            MailboxController.paginateEmails(
                                SharedStore.accounts.find(
                                    (acc) => acc.email_address === emailAddr,
                                )!,
                                prevOffsetStart,
                                prevOffsetEnd,
                            );
                        });
                    }
                };

                const clearWaitPrevInterval = () => {
                    if (waitPrev) {
                        clearInterval(waitPrev);
                        waitPrev = null;
                    }
                };

                if (currentMailbox.emails.prev.length > 0) {
                    shiftEmailPagesBackward();
                    clearWaitPrevInterval();
                    resolve();
                } else {
                    const startTime = Date.now();
                    waitPrev = setInterval(() => {
                        if (
                            Date.now() - startTime >=
                            WAIT_FOR_EMAILS_TIMEOUT_MS
                        ) {
                            clearWaitPrevInterval();
                            resolve();
                        }
                        if (currentMailbox.emails.prev.length > 0) {
                            shiftEmailPagesBackward();
                            clearWaitPrevInterval();
                            resolve();
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
                }
            }
        });
    }

    let waitNext: ReturnType<typeof setInterval> | null;

    export async function paginateMailboxForward(
        currentOffset: number,
    ): Promise<void> {
        if (currentOffset >= currentMailbox.total) return;

        return new Promise((resolve) => {
            if (!waitNext) {
                const MAILBOX_LENGTH = Number(SharedStore.preferences.mailboxLength);

                const emailAddrs =
                    SharedStore.currentAccount !== "home"
                        ? [SharedStore.currentAccount.email_address]
                        : SharedStore.accounts.filter((acc) => {
                              return (
                                  SharedStore.mailboxes[acc.email_address]
                                      .total > currentOffset
                              );
                          });

                const shiftEmailPagesForward = () => {
                    currentMailbox.emails.prev = currentMailbox.emails.current;
                    currentMailbox.emails.current = currentMailbox.emails.next;
                    currentMailbox.emails.next = [];

                    const nextOffsetStart = Math.min(
                        currentMailbox.total,
                        Math.max(1, currentOffset + MAILBOX_LENGTH * 2),
                    );
                    const nextOffsetEnd = Math.min(
                        currentMailbox.total,
                        Math.max(1, nextOffsetStart - 1 + MAILBOX_LENGTH),
                    );

                    if (nextOffsetStart <= currentMailbox.total) {
                        emailAddrs.forEach((emailAddr) => {
                            MailboxController.paginateEmails(
                                SharedStore.accounts.find(
                                    (acc) => acc.email_address === emailAddr,
                                )!,
                                nextOffsetStart,
                                nextOffsetEnd,
                            );
                        });
                    }
                };

                const clearWaitNextInterval = () => {
                    if (waitNext) {
                        clearInterval(waitNext);
                        waitNext = null;
                    }
                };

                if (currentMailbox.emails.next.length > 0) {
                    shiftEmailPagesForward();
                    clearWaitNextInterval();
                    resolve();
                } else {
                    const startTime = Date.now();
                    waitNext = setInterval(() => {
                        if (
                            Date.now() - startTime >=
                            WAIT_FOR_EMAILS_TIMEOUT_MS
                        ) {
                            clearWaitNextInterval();
                            resolve();
                        }
                        if (currentMailbox.emails.next.length > 0) {
                            shiftEmailPagesForward();
                            clearWaitNextInterval();
                            resolve();
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
                }
            }
        });
    }
</script>

<script lang="ts">
    import Context from "$lib/ui/Layout/Main/Content/Mailbox/Context.svelte";
    import Toolbox from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Mailbox/Content.svelte";
    import { setContext } from "svelte";

    setContext<MailboxContext>(CONTEXT_KEY, {
        currentOffset,
        emailSelection,
        getGroupedUidSelection: () => groupedUidSelection,
    });
</script>

<Context />
<Toolbox />
<Content />
