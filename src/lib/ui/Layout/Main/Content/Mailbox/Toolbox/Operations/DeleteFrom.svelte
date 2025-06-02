<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { isStandardFolder, simpleDeepCopy } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import {
        convertUidSelectionToMessageIds,
        fetchUidsByMessageIds,
    } from "../Operations.svelte";
    import { moveTo } from "./MoveTo.svelte";
    import type { GroupedUidSelection } from "../../../Mailbox.svelte";

    export async function deleteFrom(
        folder: string | Folder,
        groupedUidSelection: GroupedUidSelection,
        currentOffset?: number,
        isUndo: boolean = false,
    ): Promise<void> {
        const currentSelection = simpleDeepCopy(groupedUidSelection);
        const messageIdsOfSelection =
            convertUidSelectionToMessageIds(currentSelection);

        const undo = async () => {
            const newUids = await fetchUidsByMessageIds(
                Folder.Trash,
                messageIdsOfSelection,
            );
            await moveTo(Folder.Trash, folder, newUids, undefined, true);
        };

        const results = await Promise.allSettled(
            currentSelection.map(async ([email_address, uids]) => {
                const response = await MailboxController.deleteEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === email_address,
                    )!,
                    folder,
                    uids,
                    isUndo ? undefined : currentOffset,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_delete_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else if (!isStandardFolder(folder, Folder.Trash)) {
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
    import { getMailboxContext } from "../../../Mailbox";

    interface Props {
        children: Snippet;
        folder: string | Folder;
    }

    let { children, folder }: Props = $props();

    const mailboxContext = getMailboxContext();

    const deleteEmailsOnClick = async () => {
        await deleteFrom(
            folder,
            mailboxContext.getGroupedUidSelection(),
            mailboxContext.currentOffset.value,
        );
        mailboxContext.emailSelection.value = [];
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
