<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        getEmailsMarkedTemplate,
        getErrorMarkEmailsTemplate,
    } from "$lib/templates";
    import { Mark, Folder } from "$lib/types";
    import { type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { simpleDeepCopy, sortSelection } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    async function markOrUnmarkEmails(
        groupedUidSelection: GroupedUidSelection,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
        isUnmarkOperation: boolean = false,
    ) {
        const tempSelection = simpleDeepCopy(groupedUidSelection);
        const results = await Promise.allSettled(
            tempSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = sortSelection(group[1]);

                const markOperation = isUnmarkOperation
                    ? MailboxController.unmarkEmails
                    : MailboxController.markEmails;

                const response = await markOperation(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddress,
                    )!,
                    uids,
                    mark,
                    folder,
                );

                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: getErrorMarkEmailsTemplate(mark),
            });
            failed.forEach((f) => console.error(f.reason));
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: getEmailsMarkedTemplate(mark),
                onUndo: async () => {
                    groupedUidSelection = tempSelection;
                    const undoMarkOperation = isUnmarkOperation
                        ? markEmails
                        : unmarkEmails;
                    await undoMarkOperation(
                        groupedUidSelection,
                        mark,
                        folder,
                        true,
                    );
                },
            });
        }
    }

    export const markEmails = async (
        groupedUidSelection: GroupedUidSelection,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
    ) => {
        await markOrUnmarkEmails(groupedUidSelection, mark, folder, isUndo);
    };

    export const unmarkEmails = async (
        groupedUidSelection: GroupedUidSelection,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
    ) => {
        await markOrUnmarkEmails(
            groupedUidSelection,
            mark,
            folder,
            isUndo,
            true,
        );
    };
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";

    interface Props {
        children: Snippet;
        markType: Mark;
        folder: string | Folder;
        isUnmark?: boolean;
    }

    let { children, markType, folder, isUnmark = false }: Props = $props();

    const mailboxContext = getMailboxContext();

    const markEmailsOnClick = async () => {
        await markEmails(
            mailboxContext.getGroupedUidSelection(),
            markType,
            folder,
        );
        mailboxContext.emailSelection.value = [];
    };

    const unmarkEmailsOnClick = async () => {
        await unmarkEmails(
            mailboxContext.getGroupedUidSelection(),
            markType,
            folder,
        );
        mailboxContext.emailSelection.value = [];
    };
</script>

<div class="tool">
    {#if isUnmark}
        <Button.Action
            type="button"
            class="btn-inline"
            onclick={unmarkEmailsOnClick}
        >
            {@render children()}
        </Button.Action>
    {:else}
        <Button.Action
            type="button"
            class="btn-inline"
            onclick={markEmailsOnClick}
        >
            {@render children()}
        </Button.Action>
    {/if}
</div>
