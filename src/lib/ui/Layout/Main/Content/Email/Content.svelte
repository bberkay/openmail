<script lang="ts">
    import { onMount, onDestroy, mount, unmount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { create, BaseDirectory } from "@tauri-apps/plugin-fs";
    import {
        ATTACHMENT_TEMPLATE,
        SENDER_TO_RECEIVER_AND_OTHERS_TEMPLATE,
        SENDER_TO_RECEIVER_TEMPLATE,
    } from "$lib/constants";
    import { type Account, type Email } from "$lib/types";
    import {
        extractEmailAddress,
        extractFullname,
        makeSizeHumanReadable,
    } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import Badge from "$lib/ui/Components/Badge";
    import Others from "./Others.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    interface Props {
        account: Account;
        email: Email;
    }

    let { account, email }: Props = $props();

    let body: HTMLElement;
    let senderToReceiver: HTMLElement;
    let mountedOthers: Record<string, any> | null = null;
    onMount(() => {
        renderBody();

        const others = senderToReceiver.querySelector<HTMLElement>(".others");
        if (others) {
            mountedOthers = mount(Others, {
                target: others,
                props: {
                    toggleText: others.innerText,
                    receivers: email.receivers,
                    cc: email.cc,
                    bcc: email.bcc,
                },
            });
        }
    });

    onDestroy(() => {
        if (mountedOthers) {
            unmount(mountedOthers);
        }
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
        const response = await MailboxController.downloadAttachment(
            account,
            SharedStore.mailboxes[account.email_address].folder,
            email.uid,
            attachment.name,
            attachment.cid || undefined,
        );

        if (!response.success || !response.data) {
            showMessage({
                content: "Error, attachment could not be downloaded properly.",
            });
            console.error(response.message);
            return;
        }

        const file = await create(response.data.name, {
            baseDir: BaseDirectory.Download,
        });
        await file.write(
            Uint8Array.from(atob(response.data.data), (char) =>
                char.charCodeAt(0),
            ),
        );
        await file.close();
    };
</script>

<div class="email-content">
    <div class="tags">
        {#if Object.hasOwn(email, "flags") && email.flags}
            {#each email.flags as flag}
                <Badge content={flag} />
            {/each}
        {/if}
    </div>
    <div class="subject">
        {email.subject || ""}
    </div>
    <div class="sender-to-receiver" bind:this={senderToReceiver}>
        {(email.receivers.split(",").length > 1 || email.cc || email.bcc
            ? SENDER_TO_RECEIVER_AND_OTHERS_TEMPLATE
            : SENDER_TO_RECEIVER_TEMPLATE
        )
            .replace("{sender_fullname}", extractFullname(email.sender))
            .replace("{sender_email}", extractEmailAddress(email.sender))
            .replace(
                "{receiver_email}",
                account.email_address,
            )
            .replace("{sent_at}", email.date)
            .trim()}
    </div>
    <div class="separator"></div>
    <div class="body" bind:this={body}>
        <!-- Body iframe will be rendered on mount. -->
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
                    {ATTACHMENT_TEMPLATE.replace(
                        "{attachment_name}",
                        attachment.name,
                    )
                        .replace(
                            "{attachment_size}",
                            makeSizeHumanReadable(parseInt(attachment.size)),
                        )
                        .trim()}
                </Button.Action>
            {/each}
        </div>
    {/if}
</div>

<style>
    :global {
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
