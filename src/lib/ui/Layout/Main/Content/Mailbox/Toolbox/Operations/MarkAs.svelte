<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        getEmailsMarkedTemplate,
        getErrorMarkEmailsTemplate,
    } from "$lib/templates";
    import { Mark } from "$lib/types";
    import { getCurrentMailbox, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import {
        simpleDeepCopy,
        sortSelection,
    } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    async function markOrUnmarkEmails(
        selection: GroupedUidSelection,
        mark: Mark,
        isUndo: boolean = false,
        isUnmarkOperation: boolean = false,
    ) {
        const tempSelection = simpleDeepCopy(selection);
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
                    getCurrentMailbox().folder,
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
                    selection = tempSelection;
                    const undoMarkOperation = isUnmarkOperation
                        ? markEmails
                        : unmarkEmails;
                    await undoMarkOperation(selection, mark, true);
                },
            });
        }
    }

    export const markEmails = async (
        selection: GroupedUidSelection,
        mark: Mark,
        isUndo: boolean = false,
    ) => {
        await markOrUnmarkEmails(selection, mark, isUndo);
    };

    export const unmarkEmails = async (
        selection: GroupedUidSelection,
        mark: Mark,
        isUndo: boolean = false,
    ) => {
        await markOrUnmarkEmails(selection, mark, isUndo, true);
    };
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
        groupedUidSelection: GroupedUidSelection;
        markType: Mark;
        isUnmark?: boolean;
    }

    let {
        children,
        groupedUidSelection = $bindable(),
        markType,
        isUnmark = false
    }: Props = $props();

    const markEmailsOnClick = async () => {
        await markEmails(groupedUidSelection, markType);
    };

    const unmarkEmailsOnClick = async () => {
        await unmarkEmails(groupedUidSelection, markType);
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
