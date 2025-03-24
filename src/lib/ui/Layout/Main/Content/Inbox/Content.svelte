<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, type Account, Folder, type Mailbox } from "$lib/types";
    import {
        extractEmailAddress,
        extractFullname,
    } from "$lib/utils";
    import {
        MAILBOX_CLEAR_SELECTION_TEMPLATE,
        MAILBOX_SELECT_ALL_TEMPLATE,
        MAILBOX_SELECTION_INFO_TEMPLATE,
    } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import Badge from "$lib/ui/Components/Badge/Badge.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        emailSelection: string[];
    }

    type DateGroup =
        | "Today"
        | "Yesterday"
        | "This Week"
        | "This Month"
        | "Older";

    let { emailSelection = $bindable([]) }: Props = $props();

    let currentMailboxUids: string[] = $derived(
        SharedStore.currentMailbox.emails.map((email: TEmail) => email.uid).flat(),
    );

    let totalEmailCount = $derived(SharedStore.currentMailbox.total);
    let isAllEmailsSelected = $state(false);

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    const selectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = currentMailboxUids;
        selectAllButton.innerHTML = MAILBOX_CLEAR_SELECTION_TEMPLATE;
        selectShownCheckbox.checked = true;
        isAllEmailsSelected = true;
    };

    const deselectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = [];
        selectAllButton.innerHTML = MAILBOX_SELECT_ALL_TEMPLATE.replace(
            "{total}",
            totalEmailCount.toString(),
        );
        selectShownCheckbox.checked = false;
        isAllEmailsSelected = false;
    };

    function groupEmailsByDate() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const lastWeekStart = new Date(today);
        lastWeekStart.setDate(lastWeekStart.getDate() - 7);

        const lastMonthStart = new Date(today);
        lastMonthStart.setMonth(lastMonthStart.getMonth() - 1);

        const groupedEmails: Record<DateGroup, TEmail[]> = {
            Today: [],
            Yesterday: [],
            "This Week": [],
            "This Month": [],
            Older: [],
        };

        SharedStore.currentMailbox.emails.forEach((email: TEmail) => {
            const emailDate = new Date(email.date);
            emailDate.setHours(0, 0, 0, 0);

            if (emailDate.getTime() === today.getTime()) {
                groupedEmails["Today"].push(email);
            } else if (emailDate.getTime() === yesterday.getTime()) {
                groupedEmails["Yesterday"].push(email);
            } else if (emailDate >= lastWeekStart && emailDate < yesterday) {
                groupedEmails["This Week"].push(email);
            } else if (
                emailDate >= lastMonthStart &&
                emailDate < lastWeekStart
            ) {
                groupedEmails["This Month"].push(email);
            } else {
                groupedEmails["Older"].push(email);
            }
        });

        return groupedEmails;
    }

    function getAccountByEmail(emailOfSearchingAccount: TEmail): Account {
        return SharedStore.accounts.find((account) => {
            return account.email_address === SharedStore.mailboxes.find(
                task => task.result.emails.find(email => email === emailOfSearchingAccount)
            )!.email_address;
        })!;
    }

    function isRecentEmail(email: TEmail): boolean {
        return !!SharedStore.recentEmails.find(
            task => task.result.includes(email)
        );
    }

    const showEmailContent = async (selectedEmail: TEmail): Promise<void> => {
        let wasHome: boolean = false;
        if (SharedStore.currentAccount === "home") {
            wasHome = true;
            SharedStore.currentAccount = getAccountByEmail(selectedEmail);
        }
        const response = await MailboxController.getEmailContent(
            SharedStore.currentAccount,
            SharedStore.currentFolder,
            selectedEmail.uid
        );
        if (!response.success || !response.data) {
            showMessage({content: "Error, email content not fetch properly."});
            console.error(response.message);
            return;
        }
        showContent(Email, {
            account: SharedStore.currentAccount,
            email: response.data,
            wasHome: wasHome
        });
    };
</script>

<div class="mailbox">
    {#if emailSelection.length > 0}
        <div class="selection-info">
            <span>
                {MAILBOX_SELECTION_INFO_TEMPLATE.replace(
                    "{selection_count}",
                    (isAllEmailsSelected
                        ? totalEmailCount
                        : emailSelection.length
                    ).toString(),
                )}
            </span>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={isAllEmailsSelected
                    ? deselectAllEmails
                    : selectAllEmails}
            >
                {MAILBOX_SELECT_ALL_TEMPLATE.replace(
                    "{total}",
                    totalEmailCount.toString(),
                )}
            </Button.Basic>
        </div>
    {/if}
    {#each Object.entries(groupEmailsByDate()) as group}
        <div class="group-separator">
            <div class="timeline-label">
                <span>{group[0]}</span>
            </div>
        </div>
        <div class="email-group">
            {#each group[1] as email}
                <div
                    class="email"
                    onclick={() => {
                        showEmailContent(email);
                    }}
                    onkeydown={() => {
                        showEmailContent(email);
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="email-sender">
                        <input
                            type="checkbox"
                            class="select-email-checkbox"
                            bind:group={emailSelection}
                            value={email.uid}
                        />
                        <span>
                            {extractFullname(email.sender) ||
                                extractEmailAddress(email.sender)}
                        </span>
                        {#if isRecentEmail(email)}
                            <div class="new-message-icon">
                                <span>New</span>
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

                    &:hover {
                        background-color: var(--color-hover);
                    }

                    & .email-sender {
                        display: flex;
                        align-items: center;
                        gap: var(--spacing-xs);
                        width: 20%;

                        & .select-email-checkbox {
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
