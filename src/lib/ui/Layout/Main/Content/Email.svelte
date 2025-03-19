<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { create, BaseDirectory } from '@tauri-apps/plugin-fs';
    import { ATTACHMENT_TEMPLATE, SENDER_TO_RECEIVER_TEMPLATE } from '$lib/constants';
    import { onMount } from "svelte";
    import type { Account, Email } from "$lib/types";
    import { extractEmailAddress, extractFullname, makeSizeHumanReadable } from "$lib/utils";
    import * as Button from "$lib/ui/Elements/Button";
    import * as Dropdown from "$lib/ui/Elements/Dropdown";
    import Badge from "$lib/ui/Elements/Badge";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Elements/Message";

    const mailboxController = new MailboxController();

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email
    }: Props = $props();

    /* Email Handling */

    let body: HTMLElement;
    onMount(() => {
        renderBody();
    });

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

    const reply = () => {
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

    const forward = () => {
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
</script>

<div class="toolbox">
    <div class="toolbox-left">
        <Button.Basic
            type="button"
            class="btn-inline"
            style="margin-right: var(--spacing-sm)";
            onclick={() => {}}
        >
            Back
        </Button.Basic>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Star
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Archive
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Read / Unread
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Delete
            </Button.Basic>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Copy
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Move
            </Button.Basic>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Reply
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Forward
            </Button.Basic>
        </div>
        <div class="tool">
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={() => {}}
            >
                Reply All
            </Button.Basic>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            <Dropdown.Root>
                <Dropdown.Toggle>⋮</Dropdown.Toggle>
                {#snippet content()}
                    <Dropdown.Item onclick={() => {}}>Spam</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>Print</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>MIME</Dropdown.Item>
                    <Dropdown.Item onclick={() => {}}>Unsubscribe</Dropdown.Item>
                {/snippet}
            </Dropdown.Root>
        </div>
    </div>
    <div class="toolbox-right">
        <div class="pagination">
            <Button.Basic
                type="button"
                class="btn-inline"
            >
                Prev
            </Button.Basic>
            <span>21 of 1290</span>
            <Button.Basic
                type="button"
                class="btn-inline"
            >
                Next
            </Button.Basic>
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
    <div class="body" bind:this={body}></div>
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
