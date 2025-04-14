<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email, Folder, Mark } from "$lib/types";
    import {
        getErrorCopyEmailsTemplate,
        getErrorMarkEmailsTemplate,
        getErrorMoveEmailsTemplate,
        getErrorSearhCopiedEmailTemplate,
        getErrorSearhMovedEmailTemplate,
        getErrorUnmarkEmailsTemplate,
        getNotImplementedTemplate,
    } from "$lib/templates";
    import * as Button from "$lib/ui/Components/Button";
    import * as Select from "$lib/ui/Components/Select";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import {
        backToDefault,
        showThis as showContent,
        showThis,
    } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { isStandardFolder } from "$lib/utils";
    import type { PostResponse } from "$lib/services/ApiService";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let { account, email, currentOffset }: Props = $props();

    const currentFolder = SharedStore.mailboxes[account.email_address].folder;
    const customFolders = SharedStore.folders[account.email_address].custom;
    const inCustomFolder = customFolders.includes(currentFolder);

    async function getNewUidByMessageId(
        folder: string | Folder,
    ): Promise<string | undefined> {
        const searchResult = await MailboxController.searchEmails(
            account,
            folder,
            { message_id: [email.message_id] },
        );

        if (!searchResult.success || !searchResult.data) {
            showMessage({ title: "123" });
            console.error(searchResult.message);
            return;
        }

        return searchResult.data[account.email_address][0];
    }

    async function markAs(
        mark: string | Mark,
        isUndo: boolean = false,
    ): Promise<PostResponse> {
        const response = await MailboxController.markEmails(
            account,
            email.uid,
            mark,
            currentFolder,
        );

        if (!response.success) {
            showMessage({
                title: getErrorMarkEmailsTemplate(mark),
            });
            console.error(response.message);
        } else if (isUndo) {
            showToast({
                content: local.undo_done[DEFAULT_LANGUAGE],
            });
        } else {
            showToast({
                content: local.email_s_marked[DEFAULT_LANGUAGE],
                onUndo: () => {
                    removeMark(mark, true);
                },
            });
        }

        return response;
    }

    async function removeMark(
        mark: string | Mark,
        isUndo: boolean = false,
    ): Promise<PostResponse> {
        const response = await MailboxController.unmarkEmails(
            account,
            email.uid,
            mark,
            currentFolder,
        );

        if (!response.success) {
            showMessage({
                title: getErrorUnmarkEmailsTemplate(mark),
            });
            console.error(response.message);
        } else if (isUndo) {
            showToast({
                content: local.undo_done[DEFAULT_LANGUAGE],
            });
        } else {
            showToast({
                content: local.email_s_unmarked[DEFAULT_LANGUAGE],
                onUndo: () => {
                    markAs(mark, true);
                },
            });
        }

        return response;
    }

    const copyTo = async (
        uid: string,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        isUndo: boolean = false,
    ) => {
        const undo = async () => {
            const copiedEmailUid =
                await getNewUidByMessageId(destinationFolder);
            if (copiedEmailUid) {
                await deleteFrom(copiedEmailUid, destinationFolder, true);
            }
        };

        const response = await MailboxController.copyEmails(
            account,
            uid,
            sourceFolder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({
                title: getErrorCopyEmailsTemplate(
                    sourceFolder,
                    destinationFolder,
                ),
            });
            console.error(response.message);
            return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const moveTo = async (
        uid: string,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        isUndo: boolean = false,
    ) => {
        const undo = async () => {
            const movedEmailUid = await getNewUidByMessageId(destinationFolder);
            if (movedEmailUid) {
                await moveTo(
                    movedEmailUid,
                    destinationFolder,
                    sourceFolder,
                    true,
                );
            }
        };

        const response = await MailboxController.moveEmails(
            account,
            uid,
            sourceFolder,
            destinationFolder,
            isUndo ? undefined : currentOffset,
        );

        if (!response.success) {
            showMessage({
                title: getErrorMoveEmailsTemplate(
                    sourceFolder,
                    destinationFolder,
                ),
            });
            console.error(response.message);
            return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showContent(Mailbox);
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const deleteFrom = async (
        uid: string,
        folder: string | Folder,
        isUndo: boolean = false,
    ) => {
        const undo = async () => {
            const movedEmailUid = await getNewUidByMessageId(folder);
            if (movedEmailUid) {
                await moveTo(movedEmailUid, Folder.Trash, folder, true);
            }
        };

        const response = await MailboxController.deleteEmails(
            account,
            uid,
            folder,
            isUndo ? undefined : currentOffset,
        );

        if (!response.success) {
            showMessage({
                title: local.error_delete_email_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else if (!isStandardFolder(folder, Folder.Trash)) {
            showContent(Mailbox);
            showToast({
                content: "asas",
                onUndo: undo,
            });
        }
    };

    const unsubscribe = async () => {
        if (!email.list_unsubscribe) return;

        const response = await MailboxController.unsubscribe(
            account,
            email.list_unsubscribe!,
            email.list_unsubscribe_post,
        );

        if (!response.success) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
        } else {
            showToast({ content: "Unsubscribed" });
        }
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
                onclick={async () => {
                    await removeMark(Mark.Flagged);
                }}
            >
                {local.remove_star[DEFAULT_LANGUAGE]}
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={async () => {
                    await markAs(Mark.Flagged);
                }}
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
                onclick={async () => {
                    const response = await removeMark(Mark.Seen);
                    if (response.success) {
                        showContent(Mailbox);
                    }
                }}
            >
                {local.mark_as_unread[DEFAULT_LANGUAGE]}
            </Button.Action>
        {:else}
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={async () => {
                    await markAs(Mark.Seen);
                }}
            >
                {local.mark_as_read[DEFAULT_LANGUAGE]}
            </Button.Action>
        {/if}
    </div>
    {#if isStandardFolder(currentFolder, Folder.Archive)}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={async () => {
                    await moveTo(email.uid, Folder.Archive, Folder.Inbox);
                }}
            >
                {local.move_to_inbox[DEFAULT_LANGUAGE]}
            </Button.Action>
        </div>
    {:else}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={async () => {
                    await moveTo(email.uid, currentFolder, Folder.Archive);
                }}
            >
                {local.move_to_archive[DEFAULT_LANGUAGE]}
            </Button.Action>
        </div>
    {/if}
    <div class="tool">
        <Button.Action
            type="button"
            class="btn-inline"
            onclick={async () => {
                await deleteFrom(email.uid, currentFolder);
            }}
        >
            {isStandardFolder(currentFolder, Folder.Trash)
                ? local.delete_completely[DEFAULT_LANGUAGE]
                : local.delete[DEFAULT_LANGUAGE]}
        </Button.Action>
    </div>
    <div class="tool-separator"></div>
    <div class="tool">
        <Select.Root
            onchange={async (destinationFolder) => {
                await copyTo(email.uid, currentFolder, destinationFolder);
            }}
            placeholder={local.copy_to[DEFAULT_LANGUAGE]}
        >
            {#if inCustomFolder}
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
        <Select.Root
            onchange={async (destinationFolder) => {
                await moveTo(email.uid, currentFolder, destinationFolder);
            }}
            placeholder={local.move_to[DEFAULT_LANGUAGE]}
        >
            {#if inCustomFolder}
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
                            title: getNotImplementedTemplate(
                                local.spam[DEFAULT_LANGUAGE],
                            ),
                        });
                    }}
                >
                    {local.spam[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            title: getNotImplementedTemplate(
                                local.print[DEFAULT_LANGUAGE],
                            ),
                        });
                    }}
                >
                    {local.print[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item
                    onclick={() => {
                        showMessage({
                            title: getNotImplementedTemplate(
                                local.show_original[DEFAULT_LANGUAGE],
                            ),
                        });
                    }}
                >
                    {local.show_original[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
                <Dropdown.Item onclick={unsubscribe}>
                    {local.unsubscribe[DEFAULT_LANGUAGE]}
                </Dropdown.Item>
            </Dropdown.Content>
        </Dropdown.Root>
    </div>
</div>
