<script lang="ts">
    import { MailboxController } from "$lib/mailbox";
    import { type Account, type Email, Folder } from "$lib/types";
    import { getAttachmentTemplate } from "$lib/templates";
    import { makeSizeHumanReadable } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { FileSystem } from "$lib/internal/FileSystem";

    interface Props {
        account: Account;
        folder: string | Folder;
        email: Email;
    }

    let {
        account,
        folder,
        email
    }: Props = $props();

    const downloadAttachment = async (index: number) => {
        const attachment = email.attachments![index];
        const response = await MailboxController.downloadAttachment(
            account,
            folder,
            email.uid,
            attachment.name,
            attachment.cid || undefined,
        );

        if (!response.success || !response.data) {
            showMessage({
                title: local.error_attachment_download[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        const fileSystem = await FileSystem.getInstance();
        await fileSystem.download(response.data.name, atob(response.data.data));
    };
</script>

{#if email.attachments}
    <div id="attachments">
        {#each email.attachments as attachment, index}
            <Button.Action
                class="btn-outline"
                download={attachment.name}
                onclick={() => downloadAttachment(index)}
            >
                {getAttachmentTemplate(
                    attachment.name,
                    makeSizeHumanReadable(parseInt(attachment.size)),
                )}
            </Button.Action>
        {/each}
    </div>
{/if}
