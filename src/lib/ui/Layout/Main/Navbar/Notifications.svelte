<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, type Account, Folder } from "$lib/types";
    import { NEW_MESSAGE_TEMPLATE } from "$lib/constants";
    import {
        extractEmailAddress,
        extractFullname,
        isStandardFolder,
    } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    let isNotificationsHidden = $state(true);

    const toggleNotifications = () => {
        isNotificationsHidden = !isNotificationsHidden;
    };

    async function showMailboxOfReceiver(receiverEmailAddress: string) {
        if (receiverEmailAddress === "home") return;

        SharedStore.currentAccount = SharedStore.accounts.find(
            (acc) => acc.email_address == receiverEmailAddress,
        )!;

        if (
            isStandardFolder(
                SharedStore.mailboxes[SharedStore.currentAccount.email_address]
                    .folder,
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
                content: "Error, folder could not fetch.",
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
                content: "Error, email content not fetch properly.",
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

    let notificationsContainer: HTMLElement;
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
                const receivedEmail = SharedStore.recentEmails[
                    receiverAccount.email_address
                ].find((email) => email.uid === recentEmailUid)!;
                senderEmail.addEventListener("click", async () => {
                    await replyReceivedEmail(receiverAccount, receivedEmail);
                });
            });
    });

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
            nonInboxAccounts.forEach(async (account) => {
                const response = await MailboxController.getMailbox(
                    account,
                    Folder.Inbox,
                );
                if (!response.success) {
                    showMessage({
                        content: `Error, inbox of ${account.email_address} could not retrived.`,
                    });
                    console.error(response.message);
                    return;
                }
            });
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
        for (const emailAddress in SharedStore.recentEmails) {
            if (
                !recentEmailReceiverAddress ||
                emailAddress === recentEmailReceiverAddress
            ) {
                SharedStore.recentEmails[emailAddress] =
                    SharedStore.recentEmails[emailAddress].filter(
                        (email) => email.uid !== recentEmailUid,
                    );
            }
        }
    };
</script>

<div class="notifications-container" bind:this={notificationsContainer}>
    <Button.Basic
        type="button"
        class="btn-cta nav-button"
        onclick={toggleNotifications}
    >
        <Icon name="notifications" />
    </Button.Basic>
    {#if isNotificationsHidden}
        <div class="notifications">
            <div class="notifications-header">
                <div class="title">Notifications</div>
                <div class="action">
                    <Button.Basic
                        type="button"
                        class="btn-inline"
                        onclick={clearRecentEmails}
                    >
                        Clear
                    </Button.Basic>
                </div>
            </div>
            <div class="notifications-body">
                {#each Object.entries(SharedStore.recentEmails) as entry}
                    {@const emailAddress = entry[0]}
                    {@const recentEmails = entry[1]}
                    {#each recentEmails as recentEmail}
                        <div
                            class="notification-item"
                            onclick={() => {
                                showEmailContent(emailAddress, recentEmail.uid);
                            }}
                            onkeydown={() => {
                                showEmailContent(emailAddress, recentEmail.uid);
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
                                    {NEW_MESSAGE_TEMPLATE.replace(
                                        "{sender_fullname}",
                                        extractFullname(recentEmail.sender),
                                    )
                                        .replace(
                                            "{sender_email}",
                                            extractEmailAddress(
                                                recentEmail.sender,
                                            ),
                                        )
                                        .replace(
                                            "{receiver_email}",
                                            emailAddress,
                                        )
                                        .replace("{sent_at}", recentEmail.date)
                                        .trim()}
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
                                            emailAddress,
                                            recentEmail.uid,
                                        );
                                    }}
                                >
                                    <Icon name="clear" />
                                </Button.Basic>
                            </div>
                        </div>
                    {/each}
                {:else}
                    <div class="empty"></div>
                {/each}
            </div>
            <div class="notifications-footer">
                <Button.Basic
                    type="button"
                    class="btn-inline"
                    onclick={showHome}
                >
                    Go to Home
                </Button.Basic>
            </div>
        </div>
    {/if}
</div>

<style>
    :global {
        .notifications-container {
            position: relative;

            & .notifications {
                position: absolute;
                top: var(--font-size-md);
                left: var(--font-size-md);
                border: 1px solid var(--color-border);
                border-radius: var(--radius-md);
                background-color: var(--color-bg-primary);

                & .notifications-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    & .title {
                        font-size: var(--font-size-lg);
                    }
                }

                & .notifications-body {
                    display: flex;
                    flex-direction: row;

                    &:has(.empty) {
                        justify-content: center;
                        align-items: center;
                        font-size: var(--font-size-2xl);
                        padding: var(--spacing-xl);
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
                }
            }
        }
    }
</style>
