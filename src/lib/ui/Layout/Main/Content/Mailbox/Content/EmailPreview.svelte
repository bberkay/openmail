<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { getMonths, isSameDay } from "$lib/utils";

    export function findAccountByEmail(email: TEmail): Account | undefined {
        if (SharedStore.currentAccount !== "home") {
            return SharedStore.currentAccount;
        }

        return SharedStore.accounts.find((acc) =>
            SharedStore.mailboxes[acc.email_address].emails.current.find(
                (em) => em.uid === email.uid,
            ),
        );
    }

    export function isRecentEmail(account: Account, email: TEmail): boolean {
        return (
            Object.hasOwn(
                SharedStore.recentEmailsChannel,
                account.email_address,
            ) &&
            SharedStore.recentEmailsChannel[account.email_address].findIndex(
                (em) => em.uid === email.uid,
            ) !== -1
        );
    }
</script>

<script lang="ts">
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, type Account } from "$lib/types";
    import { extractEmailAddress, extractFullname, truncate } from "$lib/utils";
    import {
        getCurrentMailbox,
        type EmailSelection,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import Badge from "$lib/ui/Components/Badge/Badge.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    const MAX_BODY_LENGTH = 150;

    interface Props {
        emailSelection: EmailSelection;
        email: TEmail;
    }

    let { emailSelection = $bindable(), email }: Props = $props();
    const account = $state(findAccountByEmail(email)!);

    function compactEmailDate(emailDateStr: string) {
        const inputDate = new Date(emailDateStr);
        const currentDate = new Date();
        const months = getMonths();

        const hours = inputDate.getUTCHours().toString().padStart(2, "0");
        const minutes = inputDate.getUTCMinutes().toString().padStart(2, "0");
        const timeFormat = `${hours}:${minutes}`;

        const isToday = isSameDay(inputDate, currentDate);
        const isYesterday = isSameDay(
            inputDate,
            new Date(currentDate.getTime() - 86400000),
        ); // 24 hours in milliseconds

        const day = inputDate.getUTCDate();
        const month = months[inputDate.getUTCMonth()];
        const year = inputDate.getUTCFullYear();
        const currentYear = currentDate.getFullYear();

        if (isToday || isYesterday) {
            return timeFormat;
        } else if (year === currentYear) {
            return `${day} ${month} ${timeFormat}`;
        } else {
            return `${day} ${month} ${year}`;
        }
    }

    const showEmailContent = async (): Promise<void> => {
        const response = await MailboxController.getEmailContent(
            account,
            getCurrentMailbox().folder,
            email.uid,
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

    const deselectAllAccounts = (e: Event) => {
        e.stopPropagation();
    };
</script>

<div
    class="email-preview"
    onclick={showEmailContent}
    onkeydown={showEmailContent}
    tabindex="0"
    role="button"
>
    <div class="email-preview-select">
        <Input.Basic
            type="checkbox"
            class="email-preview-selection"
            bind:group={emailSelection as string[]}
            onclick={deselectAllAccounts}
            value={account.email_address.concat(",", email.uid)}
        />
    </div>
    <div class="email-preview-sender">
        {extractFullname(email.sender) || extractEmailAddress(email.sender)}
    </div>
    {#if isRecentEmail(account, email)}
        <div class="new-message-icon">
            {local.new[DEFAULT_LANGUAGE]}
        </div>
    {/if}
    <div class="email-preview-message">
        {#if Object.hasOwn(email, "attachments") && email.attachments!.length > 0}
            <div class="attachment-icon">
                <Icon name="attachment" />
            </div>
        {/if}
        <div class="email-preview-message-text">
            <div class="email-preview-subject">
                {email.subject}
            </div>
            <span class="subject-body-separator">---</span>
            <div class="email-preview-body">
                {truncate(email.body, MAX_BODY_LENGTH)}
            </div>
        </div>
        <div class="tags email-preview-tags">
            {#if Object.hasOwn(email, "flags") && email.flags!.length > 0}
                {#each email.flags! as flag}
                    <Badge content={flag} />
                {/each}
            {/if}
        </div>
    </div>
    <div class="email-preview-date">
        <span>{compactEmailDate(email.date)}</span>
    </div>
</div>

<style>
    :global {
        .mailbox .email-preview-group {
            display: flex;
            flex-direction: column;

            &:last-child {
                & .email-preview:last-child {
                    border-bottom: none;
                }
            }

            & .email-preview {
                display: flex;
                flex-direction: row;
                padding: var(--spacing-sm) var(--spacing-md);
                border-bottom: 1px solid var(--color-border-subtle);
                cursor: pointer;
                font-size: var(--font-size-sm);
                align-items: center;

                &:has(.email-preview-selection:checked) {
                    background-color: var(--color-border-subtle);
                }

                &:hover {
                    background-color: var(--color-hover);
                }

                & .email-preview-select {
                    display: flex;
                }

                & .email-preview-selection {
                    margin-right: 15px;
                }

                & .email-preview-sender {
                    width: 25vh;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }

                & .new-message-icon {
                    font-size: var(--font-size-xs);
                    padding: 0px var(--spacing-xs);
                    color: var(--color-white);
                    background-color: var(--color-info);
                    border-radius: var(--radius-sm);
                    font-weight: var(--font-weight-bold);
                }

                & .email-preview-message {
                    width: 100%;
                    margin-left: 3%;
                    margin-right: 3%;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;

                    & .email-preview-message-text {
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        gap: var(--spacing-xs);
                        margin-top: 4px;
                    }

                    & .subject-body-separator {
                        color: var(--color-text-secondary);
                    }

                    & .email-preview-body {
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        color: var(--color-text-secondary);
                    }

                    & .attachment-icon {
                        margin-left: calc(-1 * var(--spacing-lg));
                    }
                }

                & .email-preview-date {
                    text-align: right;
                    color: var(--color-text-secondary);
                    white-space: nowrap;
                }
            }
        }
    }
</style>
