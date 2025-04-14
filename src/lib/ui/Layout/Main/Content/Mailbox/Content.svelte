<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        type Email as TEmail,
        type Account,
        type Mailbox,
        Folder,
    } from "$lib/types";
    import { extractEmailAddress, extractFullname, isStandardFolder } from "$lib/utils";
    import {
    getEmptyTrashTemplate,
        getMailboxClearSelectionTemplate,
        getMailboxSelectAllTemplate,
        getMailboxSelectionInfoTemplate,
    } from "$lib/templates";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Badge from "$lib/ui/Components/Badge/Badge.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        emailSelection: "1:*" | string[];
    }

    type DateGroup =
        | (typeof local.today)[typeof DEFAULT_LANGUAGE]
        | (typeof local.yesterday)[typeof DEFAULT_LANGUAGE]
        | (typeof local.this_week)[typeof DEFAULT_LANGUAGE]
        | (typeof local.this_month)[typeof DEFAULT_LANGUAGE]
        | (typeof local.older)[typeof DEFAULT_LANGUAGE];

    let { emailSelection = $bindable([]) }: Props = $props();

    let groupedEmailsByDate: Record<DateGroup, TEmail[]> = $derived.by(() => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const lastWeekStart = new Date(today);
        lastWeekStart.setDate(lastWeekStart.getDate() - 7);

        const lastMonthStart = new Date(today);
        lastMonthStart.setMonth(lastMonthStart.getMonth() - 1);

        const groupedEmails: Record<DateGroup, TEmail[]> = {
            [local.today[DEFAULT_LANGUAGE]]: [],
            [local.yesterday[DEFAULT_LANGUAGE]]: [],
            [local.this_week[DEFAULT_LANGUAGE]]: [],
            [local.this_month[DEFAULT_LANGUAGE]]: [],
            [local.older[DEFAULT_LANGUAGE]]: [],
        };

        getCurrentMailbox().emails.current.forEach((email: TEmail) => {
            const emailDate = new Date(email.date);
            emailDate.setHours(0, 0, 0, 0);

            if (emailDate.getTime() === today.getTime()) {
                groupedEmails[local.today[DEFAULT_LANGUAGE]].push(email);
            } else if (emailDate.getTime() === yesterday.getTime()) {
                groupedEmails[local.yesterday[DEFAULT_LANGUAGE]].push(email);
            } else if (emailDate >= lastWeekStart && emailDate < yesterday) {
                groupedEmails[local.this_week[DEFAULT_LANGUAGE]].push(email);
            } else if (
                emailDate >= lastMonthStart &&
                emailDate < lastWeekStart
            ) {
                groupedEmails[local.this_month[DEFAULT_LANGUAGE]].push(email);
            } else {
                groupedEmails[local.older[DEFAULT_LANGUAGE]].push(email);
            }
        });

        return groupedEmails;
    });

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    function getAccountByEmail(email: TEmail): Account {
        if (SharedStore.currentAccount === "home") {
            return SharedStore.accounts.find((acc) => {
                return SharedStore.mailboxes[
                    acc.email_address
                ].emails.current.find((em) => em.uid === email.uid);
            })!;
        } else {
            return SharedStore.currentAccount;
        }
    }

    function isRecentEmail(account: Account, email: TEmail): boolean {
        return !!SharedStore.recentEmails[account.email_address].find(
            (em) => em.uid === email.uid,
        );
    }

    const selectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = "1:*";
        selectAllButton.innerHTML = getMailboxClearSelectionTemplate();
        selectShownCheckbox.checked = true;
    };

    const deselectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = [];
        selectAllButton.innerHTML = getMailboxSelectAllTemplate(
            getCurrentMailbox().total.toString(),
        );
        selectShownCheckbox.checked = false;
    };

    const emptyTrash = async () => {
        if (!isStandardFolder(getCurrentMailbox().folder, Folder.Trash))
            return;

        showConfirm({
            title: local.are_you_certain_delete_email_s[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_delete[DEFAULT_LANGUAGE],
            onConfirm: async () => {
                const response = await MailboxController.deleteEmails(
                    SharedStore.currentAccount as Account,
                    "1:*",
                    Folder.Trash
                );

                if (!response.success) {
                    showMessage({
                        title: local.error_empty_trash[DEFAULT_LANGUAGE],
                    });
                    console.error(response.message);
                } else {
                    showToast({ content: "All emails deleted" });
                }
            }
        });
    }

    const showEmailContent = async (
        account: Account,
        selectedEmail: TEmail,
    ): Promise<void> => {
        const response = await MailboxController.getEmailContent(
            account,
            getCurrentMailbox().folder,
            selectedEmail.uid,
        );

        if (!response.success || !response.data) {
            showMessage({
                title: local.error_get_email_content[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        showContent(Email, {
            account: account,
            email: response.data,
        });
    };
</script>

<div class="mailbox">
    {#if isStandardFolder(getCurrentMailbox().folder, Folder.Trash) && getCurrentMailbox().total > 0}
        <div class="selection-info">
            <span>
                {getEmptyTrashTemplate(getCurrentMailbox().total)}
            </span>
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={emptyTrash}
            >
                {local.empty_trash[DEFAULT_LANGUAGE]}
            </Button.Action>
        </div>
    {:else if emailSelection}
        <div class="selection-info">
            <span>
                {getMailboxSelectionInfoTemplate(
                    (emailSelection === "1:*"
                        ? getCurrentMailbox().total
                        : emailSelection.length
                    ).toString(),
                )}
            </span>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={emailSelection === "1:*"
                    ? deselectAllEmails
                    : selectAllEmails}
            >
                {getMailboxSelectAllTemplate(
                    getCurrentMailbox().total.toString(),
                )}
            </Button.Basic>
        </div>
    {/if}
    {#each Object.entries(groupedEmailsByDate) as group}
        <div class="group-separator">
            <div class="timeline-label">
                <span>{group[0]}</span>
            </div>
        </div>
        <div class="email-group">
            {#each group[1] as email}
                {@const account = getAccountByEmail(email)!}
                <div
                    class="email"
                    onclick={(e) => {
                        showEmailContent(account, email);
                    }}
                    onkeydown={() => {
                        showEmailContent(account, email);
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="email-sender">
                        <input
                            type="checkbox"
                            class="email-selection-checkbox"
                            bind:group={emailSelection}
                            value={account.email_address.concat(",", email.uid)}
                        />
                        <span>
                            {extractFullname(email.sender) ||
                                extractEmailAddress(email.sender)}
                        </span>
                        {#if isRecentEmail(account, email)}
                            <div class="new-message-icon">
                                <span>{local.new[DEFAULT_LANGUAGE]}</span>
                            </div>
                        {/if}
                    </div>
                    <div class="email-message">
                        {#if Object.hasOwn(email, "attachments") && email.attachments!.length > 0}
                            <div class="message-attachment-icon">
                                <Icon name="attachment" />
                            </div>
                        {/if}
                        <div class="message-subject">
                            <span>{email.subject}</span>
                        </div>
                        <span class="message-separator">---</span>
                        <div class="message-body">
                            <span>{email.body}</span>
                        </div>
                        <div class="tags">
                            {#if Object.hasOwn(email, "flags") && email.flags!.length > 0}
                                {#each email.flags! as flag}
                                    <Badge content={flag} />
                                {/each}
                            {/if}
                        </div>
                    </div>
                    <div class="email-date">
                        <span>{email.date}</span>
                    </div>
                </div>
            {/each}
        </div>
    {/each}
</div>

<style>
    :global {
        .mailbox {
            display: flex;
            flex-direction: column;
            width: 100%;
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);

            & .selection-info {
                width: 100%;
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                padding: var(--spacing-sm);
                padding-bottom: calc(var(--spacing-sm) / 1.3);
                text-align: center;
                background-color: var(--color-border-subtle);
                border-bottom: 1px solid var(--color-border);
            }

            & .group-separator {
                width: 100%;
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
                padding: var(--spacing-sm);
                padding-bottom: calc(var(--spacing-sm) / 1.3);
                text-align: center;
                border-bottom: 1px solid var(--color-border-subtle);

                & .timeline-label {
                    font-weight: var(--font-weight-bold);
                    text-transform: uppercase;
                }
            }

            & .email-group {
                display: flex;
                flex-direction: column;

                &:last-child {
                    & .email:last-child {
                        border-bottom: none;
                    }
                }

                & .email {
                    display: flex;
                    flex-direction: row;
                    justify-content: space-between;
                    padding: var(--spacing-sm);
                    border-bottom: 1px solid var(--color-border-subtle);
                    cursor: pointer;

                    &.context-menu-toggled {
                        background-color: var(--color-hover);
                        outline: 1px solid var(--color-border-subtle);
                    }

                    &:hover {
                        background-color: var(--color-hover);
                    }

                    & .email-sender {
                        display: flex;
                        align-items: center;
                        gap: var(--spacing-xs);
                        width: 20%;

                        & .email-selection-checkbox {
                            margin-right: var(--spacing-2xs);
                        }

                        & .new-message-icon {
                            font-size: var(--font-size-xs);
                            padding: 0px var(--spacing-xs);
                            color: var(--color-white);
                            background-color: var(--color-info);
                            border-radius: var(--radius-sm);
                            font-weight: var(--font-weight-bold);
                        }
                    }

                    & .email-message {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        gap: var(--spacing-xs);

                        & .message-separator {
                            color: var(--color-text-secondary);
                        }

                        & .message-body {
                            color: var(--color-text-secondary);
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                        }

                        & .message-attachment-icon {
                            margin-left: calc(-1 * var(--spacing-lg));
                        }
                    }

                    & .email-date {
                        color: var(--color-text-secondary);
                    }
                }
            }
        }
    }
</style>
