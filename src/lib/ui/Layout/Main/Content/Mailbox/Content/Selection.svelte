<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, Folder } from "$lib/types";
    import { isStandardFolder } from "$lib/utils";
    import {
        getEmptyTrashTemplate,
        getMailboxClearSelectionTemplate,
        getMailboxSelectAllTemplate,
        getMailboxSelectionInfoTemplate,
    } from "$lib/templates";
    import {
        getCurrentMailbox,
        type EmailSelection,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { onMount } from "svelte";

    interface Props {
        emailSelection: EmailSelection;
    }

    let { emailSelection = $bindable() }: Props = $props();

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    const selectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = "1:*";
        selectAllButton.innerHTML = getMailboxClearSelectionTemplate();
        selectShownCheckbox.checked = true;
    };

    const deselectAllEmails = (event: Event) => {
        const selectAllButton = event.target as HTMLButtonElement;
        emailSelection = [];
        selectAllButton.innerHTML = getMailboxSelectAllTemplate(
            getCurrentMailbox().total.toString(),
        );
        selectShownCheckbox.checked = false;
    };

    const emptyTrash = async () => {
        if (!isStandardFolder(getCurrentMailbox().folder, Folder.Trash)) return;

        const emptyTrashWrapper = async () => {
            const response = await MailboxController.deleteEmails(
                SharedStore.currentAccount as Account,
                "1:*",
                Folder.Trash,
            );

            if (!response.success) {
                showMessage({
                    title: local.error_empty_trash[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
            } else {
                showToast({ content: "All emails deleted" });
            }
        };

        showConfirm({
            title: local.are_you_certain_delete_email_s[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_delete[DEFAULT_LANGUAGE],
            onConfirm: emptyTrashWrapper,
        });
    };
</script>

{#if isStandardFolder(getCurrentMailbox().folder, Folder.Trash) && getCurrentMailbox().total > 0}
    <div class="email-preview-selection-info">
        <span>
            {getEmptyTrashTemplate(getCurrentMailbox().total)}
        </span>
        <Button.Action type="button" class="btn-inline" onclick={emptyTrash}>
            {local.empty_trash[DEFAULT_LANGUAGE]}
        </Button.Action>
    </div>
{:else if emailSelection === "1:*" || emailSelection.length > 0}
    {@const selectionCount = (
        emailSelection === "1:*"
            ? getCurrentMailbox().total
            : emailSelection.length
    ).toString()}
    <div class="email-preview-selection-info">
        <span>
            {@html getMailboxSelectionInfoTemplate(selectionCount)}
        </span>
        <Button.Basic
            type="button"
            class="btn-inline"
            onclick={emailSelection === "1:*"
                ? deselectAllEmails
                : selectAllEmails}
        >
            {@html getMailboxSelectAllTemplate(getCurrentMailbox().total)}
        </Button.Basic>
    </div>
{/if}

<style>
    :global {
        .mailbox .email-preview-selection-info {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--spacing-xs);
            color: var(--color-text-secondary);
            font-size: var(--font-size-sm);
            padding: var(--spacing-sm);
            padding-bottom: calc(var(--spacing-sm) / 1.3);
            text-align: center;
            background-color: var(--color-border-subtle);
            border-bottom: 1px solid var(--color-border);
        }
    }
</style>
