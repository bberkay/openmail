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

    export async function moveTo(
        selection: GroupedUidSelection,
        sourceFolder: string | Folder,
        destinationFolder: string | Folder,
        isUndo: boolean = false,
        currentOffset?: number
    ): Promise<void> {
        const currentSelection = simpleDeepCopy(selection);
        const messageIdsOfSelection =
            convertUidSelectionToMessageIds(currentSelection);

        const undo = async () => {
            const newUids = await fetchUidsByMessageIds(
                messageIdsOfSelection,
                destinationFolder,
            );
            await moveTo(newUids, destinationFolder, sourceFolder, true);
        };

        const results = await Promise.allSettled(
            currentSelection.map(async ([email_address, uids]) => {
                const response = await MailboxController.moveEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === email_address,
                    )!,
                    sortSelection(uids),
                    sourceFolder,
                    destinationFolder,
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
                title: local.error_move_email_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: "move done",
                onUndo: undo,
            });
        }
    };
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../../Mailbox.svelte";

    interface Props {
        children: Snippet
        groupedUidSelection: GroupedUidSelection;
        sourceFolder: string | Folder;
        destinationFolder: string | Folder;
        currentOffset?: number;
    }

    let {
        children,
        groupedUidSelection = $bindable(),
        sourceFolder,
        destinationFolder,
        currentOffset = $bindable()
    }: Props = $props();

    const moveEmailsOnClick = async () => {
        await moveTo(
            groupedUidSelection,
            sourceFolder,
            destinationFolder,
            false,
            currentOffset
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
