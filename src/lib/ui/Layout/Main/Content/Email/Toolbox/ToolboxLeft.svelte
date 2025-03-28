<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email, Folder, Mark } from "$lib/types";
    import { NOT_IMPLEMENTED_TEMPLATE } from "$lib/constants";
    import { startsWithAnyOf } from "$lib/utils";
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

    interface Props {
        account: Account;
        email: Email;
        previouslyAtHome: boolean;
    }

    let { account, email, previouslyAtHome }: Props = $props();

    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.customFolders[
                (SharedStore.currentAccount as Account).email_address
            ]
            : []
    );
    let isEmailInCustomFolder = $derived(customFolders.includes(SharedStore.currentMailbox.folder));

    const goBack = () => {
        if (previouslyAtHome) SharedStore.currentAccount = "home";
        backToDefault();
    }

    async function markAs(mark: string | Mark) {
        const response = await MailboxController.markEmails(
            account,
            email.uid,
            mark,
            SharedStore.currentFolder,
        );
        if (!response.success) {
            showMessage({
                content: `Unexpected error while marking email as ${mark}`,
            });
            console.error(response.message);
        }
    }

    async function removeMark(mark: string | Mark) {
        const response = await MailboxController.unmarkEmails(
            account,
            email.uid,
            mark,
            SharedStore.currentFolder,
        );
        if (!response.success) {
            showMessage({
                content: `Unexpected error while marking email as ${mark}`,
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
            SharedStore.currentFolder,
            destinationFolder,
        );
        if (!response.success) {
            showMessage({ content: "Unexpected error while copying email." });
            console.error(response.message);
        }
    };

    const moveTo = async (destinationFolder: string | Folder) => {
        const response = await MailboxController.moveEmails(
            account,
            email.uid,
            SharedStore.currentFolder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({ content: "Unexpected error while moving email." });
            console.error(response.message);
            return;
        }

        SharedStore.currentFolder = destinationFolder;
        showContent(Mailbox);
    };

    const moveToArchive = async () => {
        moveTo(Folder.Archive);
    };

    const deleteFrom = async () => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                const response = await MailboxController.deleteEmails(
                    account,
                    email.uid,
                    SharedStore.currentFolder,
                );

                if (!response.success) {
                    showMessage({
                        content: "Unexpected error while deleting email.",
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
            }
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
            }
        });
    };
</script>

<div class="toolbox-left">
    <Button.Basic
        type="button"
        class="btn-inline"
        style="margin-right: var(--spacing-sm)"
        onclick={goBack}
    >
        Back
    </Button.Basic>
    <div class="tool">
        {#if Object.hasOwn(email, "flags") && email.flags && email.flags.includes(Mark.Flagged)}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsNotImportant}
            >
                Remove Star
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsImportant}
            >
                Star
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
                Mark as Unread
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={markAsRead}
            >
                Mark as Read
            </Button.Action>
        {/if}
    </div>
    <div class="tool">
        <Button.Action type="button" class="btn-inline" onclick={moveToArchive}>
            Archive
        </Button.Action>
    </div>
    <div class="tool">
        <Button.Action type="button" class="btn-inline" onclick={deleteFrom}>
            Delete
        </Button.Action>
    </div>
    <div class="tool-separator"></div>
    <div class="tool">
        <Select.Root onchange={copyTo} placeholder="Copy To">
            {#if isEmailInCustomFolder}
                <!-- Add inbox option if email is in custom folder -->
                <Select.Option value={Folder.Inbox}>
                    {Folder.Inbox}
                </Select.Option>
            {/if}
            {#each customFolders as customFolder}
                {#if customFolder !== SharedStore.currentMailbox.folder}
                    <Select.Option value={customFolder}>
                        {customFolder}
                    </Select.Option>
                {/if}
            {/each}
        </Select.Root>
    </div>
    <div class="tool">
        <Select.Root onchange={moveTo} placeholder="Move To">
            {#if isEmailInCustomFolder}
                <!-- Add inbox option if email is in custom folder -->
                <Select.Option value={Folder.Inbox}>
                    {Folder.Inbox}
                </Select.Option>
            {/if}
            {#each customFolders as customFolder}
                {#if customFolder !== SharedStore.currentMailbox.folder}
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
            Reply
        </Button.Basic>
    </div>
    <div class="tool">
        <Button.Basic type="button" class="btn-inline" onclick={forward}>
            Forward
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
                            content: NOT_IMPLEMENTED_TEMPLATE.replace(
                                "{feature}",
                                "Spam",
                            ),
                        });
                    }}
                >
                    Spam
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: NOT_IMPLEMENTED_TEMPLATE.replace(
                                "{feature}",
                                "Print",
                            ),
                        });
                    }}
                >
                    Print
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: NOT_IMPLEMENTED_TEMPLATE.replace(
                                "{feature}",
                                "Show Original",
                            ),
                        });
                    }}
                >
                    Show Original
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            content: NOT_IMPLEMENTED_TEMPLATE.replace(
                                "{feature}",
                                "Unsubscribe",
                            ),
                        });
                    }}
                >
                    Unsubcribe
                </Dropdown.Item>
            </Dropdown.Content>
        </Dropdown.Root>
    </div>
</div>
