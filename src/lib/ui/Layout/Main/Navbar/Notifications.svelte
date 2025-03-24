<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, Folder } from "$lib/types";
    import { NEW_MESSAGE_TEMPLATE } from "$lib/constants";
    import { extractEmailAddress, extractFullname } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";
    import * as Button from "$lib/ui/Components/Button";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    let isNotificationsHidden = $state(true);

    const toggleNotifications = () => {
        isNotificationsHidden = !isNotificationsHidden;
    };

    const clear = (
        emailAddress: string | null = null,
        recentEmailUid: string | null = null,
    ) => {
        SharedStore.recentEmails.forEach((task) => {
            if (!emailAddress || task.email_address === emailAddress) {
                if (recentEmailUid) {
                    task.result = task.result.filter(
                        (uid) => uid !== recentEmailUid,
                    );
                } else {
                    task.result = [];
                }
            }
        });
    };

    const showAll = () => {
        // TODO: Temporary until "HOME" is implemented.
        showContent(Inbox);
    };

    const showEmailContent = async (
        receiverEmailAddress: string,
        selectedEmail: TEmail,
    ): Promise<void> => {
        const receiverAccount = SharedStore.accounts.find(
            (acc) => acc.email_address == receiverEmailAddress,
        )!;
        const response = await MailboxController.getEmailContent(
            receiverAccount,
            Folder.Inbox,
            selectedEmail.uid,
        );
        if (!response.success || !response.data) {
            showMessage({
                content: "Error, email content not fetch properly.",
            });
            console.error(response.message);
            return;
        }

        showContent(Email, {
            account: receiverAccount,
            email: response.data,
        });
    };
</script>

<div class="notifications-container">
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
                        onclick={clear}
                    >
                        Clear
                    </Button.Basic>
                </div>
            </div>
            <div class="notifications-body">
                {#each SharedStore.recentEmails as recentEmailTask}
                    {@const recentEmails = SharedStore.mailboxes
                        .find(
                            (task) =>
                                task.email_address ===
                                recentEmailTask.email_address,
                        )!
                        .result.emails.filter((email) =>
                            recentEmailTask.result.includes(email.uid),
                        )}
                    {#each recentEmails as recentEmail}
                        {@const receiverEmailAddress =
                            SharedStore.accounts.filter((acc) =>
                                recentEmail.receivers.includes(
                                    acc.email_address,
                                ),
                            )[0].email_address}
                        <div
                            class="notification-item"
                            onclick={() => {
                                showEmailContent(
                                    receiverEmailAddress,
                                    recentEmail,
                                );
                            }}
                            onkeydown={() => {
                                showEmailContent(
                                    receiverEmailAddress,
                                    recentEmail,
                                );
                            }}
                            tabindex="0"
                            role="button"
                        >
                            >
                            <div class="body">
                                <span class="sender-to-receiver">
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
                                            receiverEmailAddress,
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
                                <Button.Basic
                                    type="button"
                                    class="btn-inline"
                                    onclick={() =>
                                        clear(
                                            receiverEmailAddress,
                                            recentEmail.uid,
                                        )}
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
                    onclick={showAll}
                >
                    Show All
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
