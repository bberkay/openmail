<script lang="ts" module>
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        getErrorMarkEmailsTemplate,
    } from "$lib/templates";
    import { Mark, type Email, type Account, Folder } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    async function markOrUnmarkEmail(
        account: Account,
        uid: string,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
        isUnmarkOperation: boolean = false,
    ) {
        const markOperation = isUnmarkOperation
            ? MailboxController.unmarkEmails
            : MailboxController.markEmails;

        const response = await markOperation(
            account,
            uid,
            mark,
            folder
        );

        if (!response.success) {
            showMessage({
                title: getErrorMarkEmailsTemplate(mark),
            });
            console.error(response.message);
            return;
        }

        if (isUndo) {
            showToast({ content: local.undo_done[DEFAULT_LANGUAGE] });
        } else {
            showToast({
                content: local.email_s_marked[DEFAULT_LANGUAGE],
                onUndo: async () => {
                    const undoMarkOperation = isUnmarkOperation
                        ? markEmail
                        : unmarkEmail;
                    undoMarkOperation(account, uid, mark, folder, true);
                },
            });
        }
    }

    export async function markEmail(
        account: Account,
        uid: string,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
    ) {
        await markOrUnmarkEmail(account, uid, mark, folder, isUndo);
    }

    export async function unmarkEmail(
        account: Account,
        uid: string,
        mark: Mark,
        folder: string | Folder,
        isUndo: boolean = false,
    ) {
        await markOrUnmarkEmail(account, uid, mark, folder, isUndo, true);
    }
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import type { Snippet } from "svelte";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    interface Props {
        children: Snippet
        account: Account;
        email: Email;
        markType: Mark;
        folder: string | Folder;
        isUnmark?: boolean;
    }

    let {
        children,
        account,
        email,
        markType,
        folder,
        isUnmark = false
    }: Props = $props();

    const markEmailOnClick = async () => {
        await markEmail(account, email.uid, markType, folder);
    };

    const unmarkEmailOnClick = async () => {
        await unmarkEmail(account, email.uid, markType, folder);
        if (markType === Mark.Seen) {
            showContent(Mailbox);
        }
    };
</script>

<div class="tool">
    {#if isUnmark}
        <Button.Action
            type="button"
            class="btn-inline"
            onclick={unmarkEmailOnClick}
        >
            {@render children()}
        </Button.Action>
    {:else}
        <Button.Action
            type="button"
            class="btn-inline"
            onclick={markEmailOnClick}
        >
            {@render children()}
        </Button.Action>
    {/if}
</div>
