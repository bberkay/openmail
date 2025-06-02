<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, type Account, Folder } from "$lib/types";
    import { getNewMessageTemplate } from "$lib/templates";
    import {
        extractEmailAddress,
        extractFullname,
        isStandardFolder,
    } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import Mailbox, {
        getMailboxContext,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    const mailboxContext = getMailboxContext();

    let notificationsContainer: HTMLElement;
    let isNotificationsHidden = $state(true);

    onMount(() => {
        notificationsContainer
            .querySelectorAll<HTMLElement>(".sender-to-receiver")
            .forEach((senderToReceiver) => {
                // Set current account to clicked receiver email then
                // show its inbox.
                const receiverEmail = senderToReceiver.querySelector(
                    ".receiver-email",
                ) as HTMLElement;
                const receiverEmailAddress = extractEmailAddress(
                    receiverEmail.innerText,
                );
                receiverEmail.addEventListener("click", () => {
                    showMailboxOfReceiver(receiverEmailAddress);
                });

                // Show compose as replying to the message sent by the clicked sender.
                const senderEmail = senderToReceiver.querySelector(
                    ".sender-email",
                ) as HTMLElement;
                const recentEmailUid = (
                    senderToReceiver.querySelector(".uid") as HTMLElement
                ).innerText.trim();
                const receiverAccount = SharedStore.accounts.find(
                    (acc) => acc.email_address === receiverEmailAddress,
                )!;
                const receivedEmail = SharedStore.recentEmailsChannel[
                    receiverAccount.email_address
                ].find((email) => email.uid === recentEmailUid)!;
                senderEmail.addEventListener("click", async () => {
                    await replyReceivedEmail(receiverAccount, receivedEmail);
                });
            });
    });

    async function showMailboxOfReceiver(receiverEmailAddress: string) {
        if (receiverEmailAddress === "home") return;

        SharedStore.currentAccount = SharedStore.accounts.find(
            (acc) => acc.email_address == receiverEmailAddress,
        )!;

        if (
            isStandardFolder(
                mailboxContext.getCurrentMailbox().folder,
                Folder.Inbox,
            )
        )
            return;

        const response = await MailboxController.getMailbox(
            SharedStore.currentAccount,
            Folder.Inbox,
        );
        if (!response.success) {
            showMessage({
                title: local.error_get_mailbox[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        showContent(Mailbox);
    }

    async function getEmailContent(account: Account, uid: string) {
        const response = await MailboxController.getEmailContent(
            account,
            Folder.Inbox,
            uid,
        );
        if (!response.success || !response.data) {
            showMessage({
                title: local.error_get_email_content[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }
        return response.data;
    }

    async function replyReceivedEmail(
        receiverAccount: Account,
        receivedEmail: TEmail,
    ) {
        showContent(Compose, {
            message: {
                composeType: "reply",
                originalMessageId: receivedEmail.message_id,
                originalSender: receivedEmail.sender,
                originalReceivers: receivedEmail.receivers,
                originalSubject: receivedEmail.subject,
                originalBody: (await getEmailContent(
                    receiverAccount,
                    receivedEmail.uid,
                ))!.body,
                originalDate: receivedEmail.date,
            },
        });
    }

    const showHome = async (): Promise<void> => {
        if (SharedStore.currentAccount === "home") return;

        SharedStore.currentAccount = "home";

        const nonInboxAccounts: Account[] = [];
        for (const emailAddr in SharedStore.mailboxes) {
            if (
                !isStandardFolder(
                    SharedStore.mailboxes[emailAddr].folder,
                    Folder.Inbox,
                )
            ) {
                nonInboxAccounts.push(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddr,
                    )!,
                );
            }
        }

        if (nonInboxAccounts.length >= 1) {
            const results = await Promise.allSettled(
                nonInboxAccounts.map(async (account) => {
                    const response = await MailboxController.getMailbox(
                        account,
                        Folder.Inbox,
                    );
                    if (!response.success) {
                        throw new Error(response.message);
                    }
                }),
            );

            const failed = results.filter((r) => r.status === "rejected");

            if (failed.length > 0) {
                showMessage({
                    title: local.error_show_home[DEFAULT_LANGUAGE],
                });
                failed.forEach((f) => console.error(f.reason));
                return;
            }
        }

        showContent(Mailbox);
    };

    const showEmailContent = async (
        receiverEmailAddress: string,
        uid: string,
    ): Promise<void> => {
        const account = SharedStore.accounts.find(
            (acc) => acc.email_address == receiverEmailAddress,
        )!;

        const email = await getEmailContent(account, uid);
        if (!email) return;

        showContent(Email, {
            account,
            email,
        });
    };

    const clearRecentEmails = (
        recentEmailReceiverAddress?: string,
        recentEmailUid?: string,
    ) => {
        for (const emailAddress in SharedStore.recentEmailsChannel) {
            if (
                !recentEmailReceiverAddress ||
                emailAddress === recentEmailReceiverAddress
            ) {
                SharedStore.recentEmailsChannel[emailAddress] =
                    SharedStore.recentEmailsChannel[emailAddress].filter(
                        (email) => email.uid !== recentEmailUid,
                    );
            }
        }
    };

    const toggleNotifications = () => {
        isNotificationsHidden = !isNotificationsHidden;
    };

    const closeWhenClickedOutside = (e: Event) => {
        if (
            !isNotificationsHidden &&
            !notificationsContainer.contains(e.target as HTMLElement)
        ) {
            isNotificationsHidden = true;
        }
    };
</script>

<svelte:window onclick={closeWhenClickedOutside} />

<div class="notifications-container" bind:this={notificationsContainer}>
    <Button.Basic
        type="button"
        class="btn-inline notification-btn"
        onclick={toggleNotifications}
    >
        <Icon name="notifications" />
    </Button.Basic>
    {#if !isNotificationsHidden}
        <div class="notifications left">
            <div class="notifications-header">
                <div class="title">{local.notifications[DEFAULT_LANGUAGE]}</div>
                <div class="action">
                    <Button.Basic
                        type="button"
                        class="btn-inline"
                        onclick={clearRecentEmails}
                    >
                        <Icon name="trash" />
                    </Button.Basic>
                </div>
            </div>
            <div class="notifications-body">
                {#each Object.entries(SharedStore.recentEmailsChannel) as [email_address, recentEmails]}
                    {#each recentEmails as recentEmail}
                        <div
                            class="notification-item"
                            onclick={() => {
                                showEmailContent(
                                    email_address,
                                    recentEmail.uid,
                                );
                            }}
                            onkeydown={() => {
                                showEmailContent(
                                    email_address,
                                    recentEmail.uid,
                                );
                            }}
                            tabindex="0"
                            role="button"
                        >
                            <div class="body">
                                <span class="sender-to-receiver">
                                    <span class="uid hidden">
                                        {recentEmail.uid}
                                    </span>
                                    <span class="receivers hidden">
                                        {recentEmail.receivers}
                                    </span>
                                    {getNewMessageTemplate(
                                        extractFullname(recentEmail.sender),
                                        extractEmailAddress(recentEmail.sender),
                                        email_address,
                                        recentEmail.date,
                                    )}
                                </span>
                                <span class="message">
                                    {#if recentEmail.attachments && recentEmail.attachments.length > 0}
                                        <Icon name="attachment" />
                                    {/if}
                                    <span>{recentEmail.body}</span>
                                </span>
                            </div>
                            <div class="action">
                                <!-- TODO: Make a reply and/or forward inline button -->
                                <Button.Basic
                                    type="button"
                                    class="btn-inline"
                                    onclick={() => {
                                        clearRecentEmails(
                                            email_address,
                                            recentEmail.uid,
                                        );
                                    }}
                                >
                                    <Icon name="trash" />
                                </Button.Basic>
                            </div>
                        </div>
                    {/each}
                {:else}
                    <div class="empty">All clear!</div>
                {/each}
            </div>
            <div class="notifications-footer">
                <Button.Basic
                    type="button"
                    class="btn-inline"
                    onclick={showHome}
                >
                    {local.go_to_home[DEFAULT_LANGUAGE]}
                </Button.Basic>
            </div>
        </div>
    {/if}
</div>

<style>
    :global {
        .notifications-container {
            position: relative;

            & .notification-btn {
                & svg {
                    width: var(--font-size-lg);
                    height: var(--font-size-lg);
                }
            }

            & .notifications {
                position: absolute;
                border: 1px solid var(--color-border);
                border-radius: var(--radius-md);
                background-color: var(--color-bg-primary);
                margin-top: var(--spacing-xs);

                &.left {
                    right: 0;
                }

                & .notifications-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: var(--spacing-xs) var(--spacing-sm);

                    & .title {
                        font-size: var(--font-size-sm);
                    }
                }

                & .notifications-body {
                    display: flex;
                    flex-direction: row;
                    padding: var(--spacing-xs) var(--spacing-sm);
                    width: var(--container-sm);
                    height: var(--container-sm);
                    overflow-y: scroll;
                    overflow-x: hidden;

                    &:has(.empty) {
                        justify-content: center;
                        align-items: center;
                        font-size: var(--font-size-2xl);
                    }

                    & .notification-item {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: var(--spacing-sm);
                        border-bottom: 1px solid var(--color-border);

                        &:last-child {
                            border-bottom: none;
                        }

                        & .body {
                            display: flex;
                            flex-direction: row;
                            flex-grow: 1;

                            & .sender-to-receiver {
                                font-size: var(--font-size-xs);
                            }

                            & .message {
                                display: flex;
                                align-items: center;
                                gap: var(--spacing-2xs);
                                font-size: var(--font-size-sm);
                            }
                        }
                    }
                }

                & .notifications-footer {
                    display: flex;
                    flex: 1;
                    justify-content: center;
                    align-items: center;
                    font-size: var(--font-size-md);
                    border-top: 1px solid var(--color-border);
                    padding: var(--spacing-xs) var(--spacing-sm);
                }
            }
        }
    }
</style>
