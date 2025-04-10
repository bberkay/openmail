<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email, Folder, Mark } from "$lib/types";
    import { getErrorCopyEmailsTemplate, getErrorMarkEmailsTemplate, getErrorMoveEmailsTemplate, getErrorUnmarkEmailsTemplate, getNotImplementedTemplate } from "$lib/templates";
    import * as Button from "$lib/ui/Components/Button";
    import * as Select from "$lib/ui/Components/Select";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import {
        backToDefault,
        showThis as showContent,
    } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let {
        account,
        email,
        currentOffset
    }: Props = $props();

    const currentFolder = SharedStore.mailboxes[account.email_address].folder;
    const customFolders: string[] = SharedStore.folders[account.email_address].custom;
    const isEmailInCustomFolder = customFolders.includes(currentFolder);

    async function markAs(mark: string | Mark) {
        const response = await MailboxController.markEmails(
            account,
            email.uid,
            mark,
            currentFolder
        );
        if (!response.success) {
            showMessage({
                content: getErrorMarkEmailsTemplate(mark),
            });
            console.error(response.message);
        }
    }

    async function removeMark(mark: string | Mark) {
        const response = await MailboxController.unmarkEmails(
            account,
            email.uid,
            mark,
            currentFolder
        );
        if (!response.success) {
            showMessage({
                content: getErrorUnmarkEmailsTemplate(mark),
            });
            console.error(response.message);
        }
    }

    const markAsImportant = async (): Promise<void> => {
        await markAs(Mark.Flagged);
    };

    const markAsNotImportant = async (): Promise<void> => {
        await removeMark(Mark.Flagged);
    };

    const markAsRead = async (): Promise<void> => {
        await markAs(Mark.Seen);
    };

    const markAsUnread = async (): Promise<void> => {
        await removeMark(Mark.Seen);
        showContent(Mailbox);
    };

    const copyTo = async (destinationFolder: string | Folder) => {
        const response = await MailboxController.copyEmails(
            account,
            email.uid,
            currentFolder,
            destinationFolder,
        );
        if (!response.success) {
            showMessage({ content: getErrorCopyEmailsTemplate(currentFolder, destinationFolder) });
            console.error(response.message);
        }
    };

    const moveTo = async (destinationFolder: string | Folder) => {
        const response = await MailboxController.moveEmails(
            account,
            email.uid,
            currentFolder,
            destinationFolder,
            currentOffset
        );

        if (!response.success) {
            showMessage({ content: getErrorMoveEmailsTemplate(currentFolder, destinationFolder) });
            console.error(response.message);
            return;
        }

        SharedStore.mailboxes[account.email_address].folder = destinationFolder;
        showContent(Mailbox);
    };

    const moveToArchive = async () => {
        moveTo(Folder.Archive);
    };

    const deleteFrom = async () => {
        showConfirm({
            content: local.are_you_certain_delete_email[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_delete[DEFAULT_LANGUAGE],
            onConfirm: async (e: Event) => {
                const response = await MailboxController.deleteEmails(
                    account,
                    email.uid,
                    currentFolder,
                    currentOffset
                );

                if (!response.success) {
                    showMessage({
                        content: local.error_delete_email_s[DEFAULT_LANGUAGE]
                    });
                    console.error(response.message);
                }

                showContent(Mailbox);
            },
        });
    };

    const reply = async () => {
        showContent(Compose, {
            originalMessageContext: {
                composeType: "reply",
                originalMessageId: email.message_id,
                originalSender: email.sender,
                originalReceiver: email.receivers,
                originalSubject: email.subject,
                originalBody: email.body,
                originalDate: email.date,
            },
        });
    };

    const forward = async () => {
        showContent(Compose, {
            originalMessageContext: {
                composeType: "forward",
                originalMessageId: email.message_id,
                originalSender: email.sender,
                originalReceiver: email.receivers,
                originalSubject: email.subject,
                originalBody: email.body,
                originalDate: email.date,
            },
        });
    };
</script>

<div class="toolbox-left">
    <Button.Basic
        type="button"
        class="btn-inline"
        style="margin-right: var(--spacing-sm)"
        onclick={() => backToDefault()}
    >
        {local.back[DEFAULT_LANGUAGE]}
    </Button.Basic>
    <div class="tool">
        {#if Object.hasOwn(email, "flags") && email.flags && email.flags.includes(Mark.Flagged)}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsNotImportant}
            >
                {local.remove_star[DEFAULT_LANGUAGE]}
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsImportant}
            >
                {local.star[DEFAULT_LANGUAGE]}
            </Button.Action>
        {/if}
    </div>
    <div class="tool">
        {#if Object.hasOwn(email, "flags") && email.flags && email.flags.includes(Mark.Seen)}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsUnread}
            >
                {local.mark_as_unread[DEFAULT_LANGUAGE]}
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsRead}
            >
                {local.mark_as_read[DEFAULT_LANGUAGE]}
            </Button.Action>
        {/if}
    </div>
    <div class="tool">
        <Button.Action type="button" class="btn-inline" onclick={moveToArchive}>
            {local.archive[DEFAULT_LANGUAGE]}
        </Button.Action>
    </div>
    <div class="tool">
        <Button.Action type="button" class="btn-inline" onclick={deleteFrom}>
            {local.delete[DEFAULT_LANGUAGE]}
        </Button.Action>
    </div>
    <div class="tool-separator"></div>
    <div class="tool">
        <Select.Root onchange={copyTo} placeholder={local.copy_to[DEFAULT_LANGUAGE]}>
            {#if isEmailInCustomFolder}
                <!-- Add inbox option if email is in custom folder -->
                <Select.Option value={Folder.Inbox}>
                    {Folder.Inbox}
                </Select.Option>
            {/if}
            {#each customFolders as customFolder}
                {#if customFolder !== currentFolder}
                    <Select.Option value={customFolder}>
                        {customFolder}
                    </Select.Option>
                {/if}
            {/each}
        </Select.Root>
    </div>
    <div class="tool">
        <Select.Root onchange={moveTo} placeholder={local.move_to[DEFAULT_LANGUAGE]}>
            {#if isEmailInCustomFolder}
                <!-- Add inbox option if email is in custom folder -->
                <Select.Option value={Folder.Inbox}>
                    {Folder.Inbox}
                </Select.Option>
            {/if}
            {#each customFolders as customFolder}
                {#if customFolder !== currentFolder}
                    <Select.Option value={customFolder}>
                        {customFolder}
                    </Select.Option>
                {/if}
            {/each}
        </Select.Root>
    </div>
    <div class="tool-separator"></div>
    <div class="tool">
        <Button.Basic type="button" class="btn-inline" onclick={reply}>
            {local.reply[DEFAULT_LANGUAGE]}
        </Button.Basic>
    </div>
    <div class="tool">
        <Button.Basic type="button" class="btn-inline" onclick={forward}>
            {local.forward[DEFAULT_LANGUAGE]}
        </Button.Basic>
    </div>
    <div class="tool-separator"></div>
    <div class="tool">
        <Dropdown.Root>
            <Dropdown.Toggle>⋮</Dropdown.Toggle>
            <Dropdown.Content>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: getNotImplementedTemplate(local.spam[DEFAULT_LANGUAGE]),
                        });
                    }}
                >
                    {local.spam[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: getNotImplementedTemplate(local.print[DEFAULT_LANGUAGE]),
                        });
                    }}
                >
                    {local.print[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: getNotImplementedTemplate(local.show_original[DEFAULT_LANGUAGE]),
                        });
                    }}
                >
                    {local.show_original[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: getNotImplementedTemplate(local.unsubscribe[DEFAULT_LANGUAGE]),
                        });
                    }}
                >
                    {local.unsubscribe[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
            </Dropdown.Content>
        </Dropdown.Root>
    </div>
</div>
