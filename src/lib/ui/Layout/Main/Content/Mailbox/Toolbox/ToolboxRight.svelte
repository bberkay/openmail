<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Mailbox } from "$lib/types";
    import {
        MailboxController,
        MAILBOX_LENGTH,
    } from "$lib/controllers/MailboxController";
    import { MAILBOX_PAGINATION_TEMPLATE } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        currentMailbox: Mailbox;
    }

    let { currentMailbox }: Props = $props();

    let currentOffset = $state(1);
    let waitPrev: ReturnType<typeof setInterval> | null;
    let waitNext: ReturnType<typeof setInterval> | null;

    const getPreviousEmails = async (): Promise<void> => {
        if (currentOffset <= MAILBOX_LENGTH) return;
        if (!waitPrev) {
            const emailAddrs =
                SharedStore.currentAccount !== "home"
                    ? [SharedStore.currentAccount.email_address]
                    : SharedStore.accounts.map((acc) => acc.email_address);

            waitPrev = setInterval(() => {
                if (currentMailbox.emails.prev.length >= MAILBOX_LENGTH) {
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
                    currentOffset = Math.max(1, currentOffset - MAILBOX_LENGTH);
                    clearInterval(waitPrev!);
                    waitPrev = null;
                }
            }, 100);
        }
    };

    const getNextEmails = async (): Promise<void> => {
        if (currentOffset >= currentMailbox.total) return;
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

            waitNext = setInterval(() => {
                if (currentMailbox.emails.next.length >= MAILBOX_LENGTH) {
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
                    currentOffset = Math.min(
                        currentMailbox.total,
                        currentOffset + MAILBOX_LENGTH,
                    );
                    clearInterval(waitNext!);
                    waitNext = null;
                }
            }, 100);
        }
    };
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset <= MAILBOX_LENGTH
                ? 'disabled'
                : ''}"
            onclick={getPreviousEmails}
        >
            Prev
        </Button.Action>
        <small>
            {MAILBOX_PAGINATION_TEMPLATE.replace(
                "{offset_start}",
                currentOffset.toString(),
            )
                .replace(
                    "{offset_end}",
                    (currentOffset - 1 + MAILBOX_LENGTH).toString(),
                )
                .replace("{total}", currentMailbox.total.toString())
                .trim()}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= currentMailbox.total
                ? 'disabled'
                : ''}"
            onclick={getNextEmails}
        >
            Next
        </Button.Action>
    </div>
</div>
