<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Mailbox, Folder } from "$lib/types";
    import {
        MailboxController,
        MAILBOX_LENGTH,
    } from "$lib/controllers/MailboxController";

    const PAGINATE_MAILBOX_CHECK_DELAY = 100;

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

    export async function paginateMailboxBackward(currentOffset: number): Promise<number> {
        if (currentOffset <= MAILBOX_LENGTH)
            return currentOffset;

        return new Promise((resolve) => {
            if (!waitPrev) {
                const emailAddrs =
                    SharedStore.currentAccount !== "home"
                        ? [SharedStore.currentAccount.email_address]
                        : SharedStore.accounts.map((acc) => acc.email_address);

                const processPrevBatch = () => {
                    // TODO: Description
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

                    return Math.max(1, currentOffset - MAILBOX_LENGTH);
                }

                if (currentMailbox.emails.prev.length >= MAILBOX_LENGTH) {
                    resolve(processPrevBatch());
                } else {
                    waitPrev = setInterval(() => {
                        if (currentMailbox.emails.prev.length >= MAILBOX_LENGTH) {
                            const updatedOffset = processPrevBatch();
                            clearInterval(waitPrev!);
                            waitPrev = null;
                            resolve(updatedOffset);
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY);
                }
            }
        });
    }

    export async function paginateMailboxForward(currentOffset: number): Promise<number> {
        if (currentOffset >= currentMailbox.total)
            return currentOffset;

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

                const processNextBatch = (): number => {
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

                    return Math.min(
                        currentMailbox.total,
                        currentOffset + MAILBOX_LENGTH,
                    );
                }

                if (currentMailbox.emails.next.length >= MAILBOX_LENGTH) {
                    resolve(processNextBatch());
                } else {
                    waitNext = setInterval(() => {
                        if (currentMailbox.emails.next.length >= MAILBOX_LENGTH) {
                            const updatedOffset = processNextBatch();
                            clearInterval(waitNext!);
                            waitNext = null;
                            resolve(updatedOffset);
                        }
                    }, PAGINATE_MAILBOX_CHECK_DELAY);
                }
            }
        })
    }
</script>

<script lang="ts">
    import Toolbox from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox.svelte";
    import Content from "$lib/ui/Layout/Main/Content/Mailbox/Content.svelte";

    let emailSelection: "1:*" | string[] = $state([]);
</script>

<Toolbox bind:emailSelection />
<Content bind:emailSelection />
