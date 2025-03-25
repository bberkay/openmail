<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { MAILBOX_LENGTH, MAILBOX_PAGINATION_TEMPLATE } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";

    let currentOffset = $state(1);
    let totalEmailCount = $derived(SharedStore.currentMailbox.total);

    const getPreviousEmails = async (): Promise<void> => {
        if (currentOffset <= MAILBOX_LENGTH) return;

        const offset_start = Math.max(1, currentOffset - MAILBOX_LENGTH);
        const offset_end = Math.max(1, currentOffset);
        const response = await MailboxController.paginateEmails(
            SharedStore.currentAccount === "home"
                ? SharedStore.accounts
                : SharedStore.currentAccount,
            offset_start,
            offset_end,
        );
        if (response.success) {
            currentOffset = Math.max(1, offset_start);
        } else {
            showMessage({ content: "Error while getting previous emails." });
            console.error(response.message);
        }
    };

    const getNextEmails = async (): Promise<void> => {
        if (currentOffset >= totalEmailCount) return;

        const offset_start = Math.min(totalEmailCount, currentOffset + MAILBOX_LENGTH);
        const offset_end = Math.min(totalEmailCount, currentOffset + MAILBOX_LENGTH * 2);
        const response = await MailboxController.paginateEmails(
            SharedStore.currentAccount === "home"
                ? SharedStore.accounts
                : SharedStore.currentAccount,
            offset_start,
            offset_end,
        );
        if (response.success) {
            currentOffset = Math.max(1, offset_start);
        } else {
            showMessage({ content: "Error while getting next emails." });
            console.error(response.message);
        }
    };
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset < MAILBOX_LENGTH ? 'disabled' : ''}"
            onclick={getPreviousEmails}
        >
            Prev
        </Button.Action>
        <small>
            {MAILBOX_PAGINATION_TEMPLATE.replace(
                "{offset_start}",
                Math.max(1, currentOffset).toString(),
            )
                .replace(
                    "{offset_end}",
                    Math.min(totalEmailCount, currentOffset + MAILBOX_LENGTH).toString(),
                )
                .replace("{total}", totalEmailCount.toString())
                .trim()}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= totalEmailCount
                ? 'disabled'
                : ''}"
            onclick={getNextEmails}
        >
            Next
        </Button.Action>
    </div>
</div>
