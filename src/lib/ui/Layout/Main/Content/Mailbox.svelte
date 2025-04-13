<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Mailbox, Folder } from "$lib/types";
    import { MAILBOX_LENGTH, PAGINATE_MAILBOX_CHECK_DELAY_MS, WAIT_FOR_EMAILS_TIMEOUT_MS } from "$lib/constants";
    import { MailboxController } from "$lib/controllers/MailboxController";

    let waitPrev: ReturnType<typeof setInterval> | null;
    let waitNext: ReturnType<typeof setInterval> | null;

    let currentMailbox = $derived.by(() => {
        if (SharedStore.currentAccount === "home") {
            let currentMailbox: Mailbox = {
                total: 0,
                emails: { prev: [], current: [], next: [] },
                folder: Folder.Inbox // mailboxes are going to be INBOX while selecting account to "home"
            };
            Object.values(SharedStore.mailboxes).forEach((mailbox) => {
                currentMailbox.total += mailbox.total;
                currentMailbox.emails.prev.push(...mailbox.emails.prev);
                currentMailbox.emails.current.push(...mailbox.emails.current);
                currentMailbox.emails.next.push(...mailbox.emails.next);
            });
            Object.values(currentMailbox.emails).forEach((emails) => {
                emails.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
            })
            return currentMailbox;
        } else {
            return SharedStore.mailboxes[
                SharedStore.currentAccount.email_address
            ]
        }
    });

    export function getCurrentMailbox() {
        return currentMailbox;
    }

    export async function paginateMailboxBackward(currentOffset: number): Promise<void> {
        if (currentOffset <= MAILBOX_LENGTH)
            return;

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
                }

                const clearWaitPrevInterval = () => {
                    if (waitPrev) {
                       clearInterval(waitPrev);
                       waitPrev = null;
                       resolve();
                    }
                }

                if (currentMailbox.emails.prev.length > 0) {
                    shiftEmailPagesBackward()
                    clearWaitPrevInterval();
                } else {
                    const startTime = Date.now();
                    waitPrev = setInterval(() => {
                        if (Date.now() - startTime >= WAIT_FOR_EMAILS_TIMEOUT_MS) {
                            clearWaitPrevInterval();
                        }
                        if (currentMailbox.emails.prev.length > 0) {
                            shiftEmailPagesBackward();
                            clearWaitPrevInterval();
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
                }
            }
        });
    }

    export async function paginateMailboxForward(currentOffset: number): Promise<void> {
        if (currentOffset >= currentMailbox.total)
            return;

        return new Promise((resolve) => {
            if (!waitNext) {
                const emailAddrs =
                    SharedStore.currentAccount !== "home"
                        ? [SharedStore.currentAccount.email_address]
                        : SharedStore.accounts.filter((acc) => {
                              return (
                                  SharedStore.mailboxes[acc.email_address].total >
                                  currentOffset
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
                }

                const clearWaitNextInterval = () => {
                    if (waitNext) {
                        clearInterval(waitNext);
                        waitNext = null;
                        resolve();
                    }
                }

                if (currentMailbox.emails.next.length > 0) {
                    shiftEmailPagesForward()
                    clearWaitNextInterval();
                } else {
                    const startTime = Date.now();
                    waitNext = setInterval(() => {
                        if (Date.now() - startTime >= WAIT_FOR_EMAILS_TIMEOUT_MS) {
                            clearWaitNextInterval();
                        }
                        if (currentMailbox.emails.next.length > 0) {
                            shiftEmailPagesForward();
                            clearWaitNextInterval();
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY_MS);
                }
            }
        })
    }
</script>

<script lang="ts">
    import Toolbox from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Mailbox/Content.svelte";

    let currentOffset = $state(1);
    let emailSelection: "1:*" | string[] = $state([]);
</script>

<Toolbox bind:emailSelection bind:currentOffset />
<Content bind:emailSelection />
