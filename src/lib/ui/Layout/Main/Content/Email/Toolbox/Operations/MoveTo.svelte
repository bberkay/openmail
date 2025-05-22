<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account, type Email } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { simpleDeepCopy, sortSelection } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { fetchUidByMessageId } from "../Operations.svelte";

    export async function moveTo(
        account: Account,
        uid: string,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        currentOffset?: number,
        message_id?: string,
        isUndo: boolean = false,
    ): Promise<void> {
        const undo = async () => {
            if (!message_id)
                throw new Error("Can't undo operation without message_id");
            const movedEmailUid = await fetchUidByMessageId(
                account,
                destinationFolder,
                message_id,
            );
            if (movedEmailUid) {
                await moveTo(
                    account,
                    movedEmailUid,
                    destinationFolder,
                    sourceFolder,
                    currentOffset,
                    message_id,
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
            showMessage({ title: "Could not move email" });
            console.error(response.message);
            return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showContent(Mailbox);
            showToast({
                content: "move done",
                onUndo: undo,
            });
        }
    }
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        account: Account;
        email: Email;
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
        currentOffset?: number;
    }

    let {
        children,
        account,
        email,
        sourceFolder,
        destinationFolder,
        currentOffset
    }: Props = $props();

    const moveEmailsOnClick = async () => {
        await moveTo(
            account,
            email.uid,
            sourceFolder,
            destinationFolder,
            currentOffset,
            email.message_id,
            false,
        );
    };
</script>

<div class="tool">
    <Button.Action
        type="button"
        class="btn-inline"
        onclick={moveEmailsOnClick}
    >
        {@render children()}
    </Button.Action>
</div>
