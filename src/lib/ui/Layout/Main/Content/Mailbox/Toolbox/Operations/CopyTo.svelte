<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import {
        simpleDeepCopy,
        sortSelection,
    } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { convertUidSelectionToMessageIds, fetchUidsByMessageIds } from "../Operations.svelte";
    import type { GroupedUidSelection } from "../../../Mailbox.svelte";

    export async function copyTo(
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        groupedUidSelection: GroupedUidSelection,
        isUndo: boolean = false,
    ): Promise<void> {
        const currentSelection = simpleDeepCopy(groupedUidSelection);
        const messageIdsOfSelection =
            convertUidSelectionToMessageIds(currentSelection);

        const undo = async () => {
            const newUids = await fetchUidsByMessageIds(
                destinationFolder,
                messageIdsOfSelection,
            );
            await deleteFrom(
                destinationFolder,
                newUids,
                undefined,
                true
            );
        };

        const results = await Promise.allSettled(
            currentSelection.map(async ([email_address, uids]) => {
                const response = await MailboxController.copyEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === email_address,
                    )!,
                    sourceFolder,
                    destinationFolder,
                    sortSelection(uids),
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_move_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: "copy done",
                onUndo: undo,
            });
        }
    };
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import { deleteFrom } from "./DeleteFrom.svelte";
    import { getMailboxContext } from "../../../Mailbox.svelte";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
    }

    let {
        children,
        sourceFolder,
        destinationFolder,
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const copyEmailsOnClick = async () => {
        await copyTo(
            sourceFolder,
            destinationFolder,
            mailboxContext.getGroupedUidSelection()
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
