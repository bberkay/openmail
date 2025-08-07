<script lang="ts" module>
    import { MailboxController } from "$lib/mailbox";
    import { Folder, type Account, type Email } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { isStandardFolder } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { fetchUidByMessageId } from "../Operations.svelte";
    import { moveTo } from "./MoveTo.svelte";

    export async function deleteFrom(
        account: Account,
        folder: string | Folder,
        uid: string,
        currentOffset?: number,
        message_id?: string,
        isUndo: boolean = false,
    ): Promise<void> {
        const undo = async () => {
            if (!message_id)
                throw new Error("Can't undo operation without message_id");
            const movedEmailUid = await fetchUidByMessageId(
                account,
                Folder.Trash,
                message_id,
            );
            if (movedEmailUid) {
                await moveTo(
                    account,
                    Folder.Trash,
                    folder,
                    movedEmailUid,
                    undefined,
                    message_id,
                    true
                );
            }
        };

        const response = await MailboxController.deleteEmails(
            account,
            folder,
            uid,
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
                content: "delete done",
                onUndo: undo,
            });
        }
    }
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        account: Account;
        folder: string | Folder;
        email: Email;
        currentOffset?: number;
    }

    let {
        children,
        account,
        folder,
        email,
        currentOffset
    }: Props = $props();

    const deleteEmailsOnClick = async () => {
        await deleteFrom(
            account,
            folder,
            email.uid,
            currentOffset,
            email.message_id,
        );
    };
</script>

<div class="tool">
    <Button.Action
        type="button"
        class="btn-inline"
        onclick={deleteEmailsOnClick}
    >
        {@render children()}
    </Button.Action>
</div>
