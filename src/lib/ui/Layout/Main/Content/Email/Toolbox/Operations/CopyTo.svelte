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
    import { deleteFrom } from "./DeleteFrom.svelte";

    export async function copyTo(
        account: Account,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        uid: string,
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
                await deleteFrom(
                    account,
                    destinationFolder,
                    movedEmailUid,
                    undefined,
                    message_id,
                    true,
                );
            }
        };

        const response = await MailboxController.copyEmails(
            account,
            sourceFolder,
            destinationFolder,
            uid,
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
                content: "copy done",
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
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
        email: Email;
    }

    let {
        children,
        account,
        sourceFolder,
        destinationFolder,
        email,
    }: Props = $props();

    const copyEmailsOnClick = async () => {
        await copyTo(
            account,
            sourceFolder,
            destinationFolder,
            email.uid,
            email.message_id,
        );
    };
</script>

<div class="tool">
    <Button.Action
        type="button"
        class="btn-inline"
        onclick={copyEmailsOnClick}
    >
        {@render children()}
    </Button.Action>
</div>
