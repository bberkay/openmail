<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { compactEmailDate } from "$lib/utils";

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
    import { onMount } from "svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email as TEmail, type Account } from "$lib/types";
    import { extractEmailAddress, extractFullname, truncate, createDomElement, generateHash } from "$lib/utils";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import Badge from "$lib/ui/Components/Badge/Badge.svelte";
    import Email from "$lib/ui/Layout/Main/Content/Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { GravatarService } from "$lib/services/GravatarService";
  
    const MAX_BODY_LENGTH = 150;

    interface Props {
        email: TEmail;
    }

    let {
        email
    }: Props = $props();

    const mailboxContext = getMailboxContext();
    const account = $state(findAccountByEmail(email)!);

    let isAvatarShown = $state(true);
    let emailAvatar: HTMLElement;

    onMount(() => {
        setupEmailAvatars();
    });

    async function setupEmailAvatars() {
        const sender = email.sender;
        const avatar = await GravatarService.getAvatar(sender);
        avatar.classList.add("avatar");
        emailAvatar.appendChild(avatar);
    }

    const showEmailContent = async (e: Event): Promise<void> => {
        const target = (e.target as HTMLElement).closest(".email-preview") as HTMLElement;
        target.setAttribute("disabled", "true");

        const response = await MailboxController.getEmailContent(
            account,
            getCurrentMailbox().folder,
            email.uid,
        );

        target.removeAttribute("disabled");
        mailboxContext.emailSelection.value = [];

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
    onmouseenter={() => isAvatarShown = false}
    onmouseleave={() => isAvatarShown = true}
    onfocus={() => isAvatarShown = false}
    onblur={() => isAvatarShown = true}
    tabindex="0"
    role="button"
>
    <div class="email-preview-selection-container">
        <div class="email-preview-avatar-container {isAvatarShown ? "" : "hidden"}" bind:this={emailAvatar}></div>
        <Input.Basic
            type="checkbox"
            class="email-preview-selection {isAvatarShown ? "hidden" : ""}"
            bind:group={mailboxContext.emailSelection.value as string[]}
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
    <div class="email-preview-content">
        {#if Object.hasOwn(email, "attachments") && email.attachments!.length > 0}
            <div class="attachment-icon">
                <Icon name="attachment" />
            </div>
        {/if}
        <div class="email-preview-message-container">
            <div class="email-preview-message">
                <div class="email-preview-subject">
                    {email.subject}
                </div>
                <span class="subject-body-separator">---</span>
                <div class="email-preview-body">
                    {truncate(email.body, MAX_BODY_LENGTH)}
                </div>
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
        .mailbox:has(.email-preview[disabled]) {
            cursor: wait!important;

            & .email-preview {
                pointer-events: none!important;
            }
        }

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
                width: 100%;

                &:has(.email-preview-selection:checked) {
                    background-color: var(--color-border-subtle);
                }

                &:hover {
                    background-color: var(--color-hover);
                }

                & .email-preview-selection-container {
                    display: flex;
                    width: 35px;

                    & .email-preview-avatar-container .avatar {
                        width: 20px;
                        height: 20px;
                        border-radius: 5px;
                        margin-bottom: -2px;
                    }

                    & .email-preview-selection {
                        margin-left: 2px;
                    }
                }

                & .email-preview-sender {
                    width: 15%;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    margin-right: 2%;
                }

                & .new-message-icon {
                    font-size: var(--font-size-xs);
                    padding: 0px var(--spacing-xs);
                    color: var(--color-white);
                    background-color: var(--color-info);
                    border-radius: var(--radius-sm);
                    font-weight: var(--font-weight-bold);
                }

                & .email-preview-content {
                    display: flex;
                    width: 75%;
                    gap: var(--spacing-md);

                    & .attachment-icon {
                        margin-left: calc(-1 * var(--spacing-lg));
                    }

                    & .email-preview-message-container {
                        width: 100%;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;

                        & .email-preview-message {
                            display: flex;
                            flex-direction: row;
                            align-items: center;
                            gap: var(--spacing-xs);
                            margin-top: 4px;

                            & .subject-body-separator {
                                color: var(--color-text-secondary);
                            }

                            & .email-preview-body {
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                color: var(--color-text-secondary);
                            }
                        }
                    }
                }

                & .email-preview-date {
                    text-align: right;
                    color: var(--color-text-secondary);
                    white-space: nowrap;
                    width: 8%;
                }
            }
        }
    }
</style>
