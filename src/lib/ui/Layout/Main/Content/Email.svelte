<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { create, BaseDirectory } from '@tauri-apps/plugin-fs';
    import { ATTACHMENT_TEMPLATE, SENDER_TO_RECEIVER_TEMPLATE, EMAIL_PAGINATION_TEMPLATE } from '$lib/constants';
    import { type Account, type Email, Folder, Mark } from "$lib/types";
    import { extractEmailAddress, extractFullname, findMatchingIndex, findMatchingObject, makeSizeHumanReadable,startsWithAnyOf } from "$lib/utils";
    import * as Button from "$lib/ui/Elements/Button";
    import * as Select from "$lib/ui/Elements/Select";
    import * as Dropdown from "$lib/ui/Elements/Dropdown";
    import Badge from "$lib/ui/Elements/Badge";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
    import { backToDefault, showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Elements/Message";
    import { show as showConfirm } from "$lib/ui/Elements/Confirm";

    const mailboxController = new MailboxController();

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email
    }: Props = $props();

    let currentMailbox = $derived(SharedStore.mailboxes.find(
        task => task.result.folder === SharedStore.currentFolder
    )!.result);
    let totalEmailCount = $derived(currentMailbox.total);
    let currentOffset = $derived(currentMailbox.emails.findIndex(
        em => em.uid === email.uid
    ) + 1);

    const isEmailInCustomFolder = SharedStore.currentFolder &&
        !startsWithAnyOf(SharedStore.currentFolder, Object.values(Folder));
    const customFoldersOfAccount = SharedStore.customFolders.find(
        acc => acc.email_address === account!.email_address
    )!.result

    /* Render Body */

    let body: HTMLElement;
    onMount(() => { renderBody() });

    function renderBody(): void {
        body.innerHTML = "";

        let iframe = document.createElement("iframe");
        body.appendChild(iframe);

        let iframeDoc: Document | null;
        iframeDoc = iframe.contentWindow
            ? iframe.contentWindow.document
            : iframe.contentDocument;
        if (iframeDoc) {
            iframeDoc.open();
            iframeDoc.writeln(email.body);
            iframeDoc.close();

            body.style.height = iframeDoc.body.scrollHeight + "px";
        }
    }

    /* Email Operations */

    const downloadAttachment = async (index: number) => {
        const attachment = email.attachments![index];
        const response = await mailboxController.downloadAttachment(
            account,
            SharedStore.currentFolder!,
            email.uid,
            attachment.name,
            attachment.cid || undefined
        );

        if (!response.success || !response.data) {
            showMessage({content: "Error, attachment could not be downloaded properly."});
            console.error(response.message);
            return;
        }

        const file = await create(response.data.name, { baseDir: BaseDirectory.Download });
        await file.write(Uint8Array.from(atob(response.data.data), (char) => char.charCodeAt(0)));
        await file.close();
    }

    /* Toolbox Operations */

    async function markAs(mark: string | Mark) {
        const response = await mailboxController.markEmails(
            account,
            [email.uid],
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            showMessage({content: `Unexpected error while marking email as ${mark}`});
            console.error(response.message);
        }
    }

    async function removeMark(mark: string | Mark) {
        const response = await mailboxController.unmarkEmails(
            account,
            [email.uid],
            mark,
            SharedStore.currentFolder
        );
        if(!response.success) {
            showMessage({content: `Unexpected error while marking email as ${mark}`});
            console.error(response.message);
        }
    }

    const markAsImportant = async (): Promise<void> => {
        await markAs(Mark.Flagged);
    }

    const markAsNotImportant = async (): Promise<void> => {
        await removeMark(Mark.Flagged);
    }

    const markAsRead = async (): Promise<void> => {
        await markAs(Mark.Seen);
    }

    const markAsUnread = async (): Promise<void> => {
        await removeMark(Mark.Seen);
    }

    const copyTo = async (destinationFolder: string) => {
        const response = await mailboxController.copyEmails(
            account,
            [email.uid],
            SharedStore.currentFolder,
            destinationFolder
        );
        if(!response.success) {
            showMessage({content: "Unexpected error while copying email."});
            console.error(response.message);
        }
    }

    const moveTo = async (destinationFolder: string) => {
        const response = await mailboxController.moveEmails(
            account,
            [email.uid],
            SharedStore.currentFolder,
            destinationFolder
        );

        if(!response.success) {
            showMessage({content: "Unexpected error while moving email."});
            console.error(response.message);
            return;
        }

        SharedStore.currentFolder = destinationFolder;
        showContent(Inbox);
    }

    const deleteFrom = async () => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                const response = await mailboxController.deleteEmails(
                    account,
                    [email.uid],
                    SharedStore.currentFolder
                );
                if(!response.success) {
                    showMessage({content: "Unexpected error while deleting email."});
                    console.error(response.message);
                }
            },
        })
    }

    const reply = async () => {
        showContent(Compose, {
            compose_type: "reply",
            original_message_id: email.message_id,
            original_sender: email.sender,
            original_receiver: email.receivers,
            original_subject: email.subject,
            original_body: email.body,
            original_date: email.date
        });
    }

    const forward = async () => {
        showContent(Compose, {
            compose_type: "forward",
            original_message_id: email.message_id,
            original_sender: email.sender,
            original_receiver: email.receivers,
            original_subject: email.subject,
            original_body: email.body,
            original_date: email.date
        })
    }

    const setEmailByUid = async (uid: string): Promise<void> => {
        const response = await mailboxController.getEmailContent(
            account,
            currentMailbox.folder,
            uid
        );

        if (!response.success || !response.data) {
            showMessage({content: "Error while getting email content."});
            console.error(response.message);
            return;
        }

        email = response.data;
    }

    const getPreviousEmail = async () => {
        const previousUidIndex = currentMailbox.emails.findIndex(
            em => em.uid === email.uid
        ) - 1;
        if (previousUidIndex < 0)
            return;

        setEmailByUid(currentMailbox.emails[previousUidIndex].uid);
    }

    const getNextEmail = async () => {
        const nextUidIndex = currentMailbox.emails.findIndex(
            em => em.uid === email.uid
        ) - 1;
        if (nextUidIndex < 0)
            return;

        setEmailByUid(currentMailbox.emails[nextUidIndex].uid);
    }
</script>

<div class="toolbox">
    <div class="toolbox-left">
        <Button.Basic
            type="button"
            class="btn-inline"
            style="margin-right: var(--spacing-sm)";
            onclick={backToDefault}
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
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={deleteFrom}
            >
                Archive
            </Button.Action>
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
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={deleteFrom}
            >
                Delete
            </Button.Action>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Select.Root onchange={copyTo} placeholder='Copy To'>
                {#each customFoldersOfAccount as customFolder}
                    <Select.Option value={customFolder}>{customFolder}</Select.Option>
                {/each}
                {#if isEmailInCustomFolder}
                    <!-- Add inbox option if email is in custom folder -->
                    <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                {/if}
            </Select.Root>
        </div>
        <div class="tool">
            <Select.Root onchange={moveTo} placeholder='Move To'>
                {#each customFoldersOfAccount as customFolder}
                    <Select.Option value={customFolder}>{customFolder}</Select.Option>
                {/each}
                {#if isEmailInCustomFolder}
                    <!-- Add inbox option if email is in custom folder -->
                    <Select.Option value={Folder.Inbox}>{Folder.Inbox}</Select.Option>
                {/if}
            </Select.Root>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={reply}
            >
                Reply
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={forward}
            >
                Forward
            </Button.Basic>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Dropdown.Root>
                <Dropdown.Toggle>⋮</Dropdown.Toggle>
                {#snippet content()}
                    <Dropdown.Item onclick={() => {}}>Spam</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>Print</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>Show Original</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>Unsubcribe</Dropdown.Item>
                {/snippet}
            </Dropdown.Root>
        </div>
    </div>
    <div class="toolbox-right">
        <div class="pagination">
            <Button.Action
                type="button"
                class="btn-inline {currentOffset < 2 ? "disabled" : ""}"
                onclick={getPreviousEmail}
            >
                Prev
            </Button.Action>
            <small>
                {
                    EMAIL_PAGINATION_TEMPLATE
                        .replace("{current}", Math.max(1, currentOffset).toString())
                        .replace("{total}", totalEmailCount.toString())
                        .trim()
                }
            </small>
            <Button.Action
                type="button"
                class="btn-inline {currentOffset >= totalEmailCount ? "disabled" : ""}"
                onclick={getNextEmail}
            >
                Next
            </Button.Action>
        </div>
    </div>
</div>

<div class="email-content">
    <div class="flags">
        {#if Object.hasOwn(email, "flags") && email.flags}
            {#each email.flags as flag}
                <Badge content={flag} />
            {/each}
        {/if}
    </div>
    <div class="subject">
        {email.subject || ""}
    </div>
    <div class="sender-to-receiver">
        {
            SENDER_TO_RECEIVER_TEMPLATE
                .replace("{sender_fullname}", extractFullname(email.sender))
                .replace("{sender_email}", extractEmailAddress(email.sender))
                .replace("{sent_at}", email.date)
                .trim()
        }
    </div>
    <div class="separator"></div>
    <div class="body" bind:this={body}>
        <!-- Body is going to be here -->
    </div>
    {#if Object.hasOwn(email, "attachments") && email.attachments}
        <div class="separator"></div>
        <div id="attachments">
            {#each email.attachments as attachment, index}
                <Button.Action
                    class="btn-outline"
                    download={attachment.name}
                    onclick={() => downloadAttachment(index)}
                >
                    {
                        ATTACHMENT_TEMPLATE
                            .replace("{attachment_name}", attachment.name)
                            .replace("{attachment_size}", makeSizeHumanReadable(parseInt(attachment.size)))
                            .trim()
                    }
                </Button.Action>
            {/each}
        </div>
    {/if}
</div>

<style>
    :global {
        .toolbox {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            padding: var(--spacing-sm) var(--spacing-lg);

            & .toolbox-left {
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: var(--spacing-xl);
            }

            & .toolbox-right {
                & .pagination {
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    font-size: var(--font-size-sm);
                    gap: var(--spacing-md);
                    color: var(--color-text-secondary);

                    & svg {
                        margin-top: var(--spacing-2xs);
                    }
                }
            }
        }

        .email-content {
            display: flex;
            flex-direction: column;
            padding: var(--spacing-lg);
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);

            & .subject {
                margin-top: var(--spacing-md);
                display: flex;
                flex-direction: column;
                font-size: var(--font-size-lg);
            }

            & .sender-to-receiver {
                margin-top: var(--spacing-xs);
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
            }
        }
    }
</style>
