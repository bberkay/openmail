<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { MAILBOX_PAGINATION_TEMPLATE } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";

    const mailboxController = new MailboxController();

    let currentMailbox = $derived(
        SharedStore.mailboxes.find(
            (task) =>
                task.email_address ===
                    SharedStore.currentAccount!.email_address &&
                task.result.folder === SharedStore.currentFolder,
        )!.result,
    );

    let currentOffset = $state(1);
    let totalEmailCount = $derived(currentMailbox.total);

    const getPreviousEmails = async (): Promise<void> => {
        if (currentOffset <= 10) return;

        const offset_start = Math.max(1, currentOffset - 10);
        const offset_end = Math.max(1, currentOffset);
        const response = await mailboxController.paginateEmails(
            SharedStore.currentAccount,
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

        const offset_start = Math.min(totalEmailCount, currentOffset + 10);
        const offset_end = Math.min(totalEmailCount, currentOffset + 10 + 10);
        const response = await mailboxController.paginateEmails(
            SharedStore.currentAccount,
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
            class="btn-inline {currentOffset < 10 ? 'disabled' : ''}"
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
                    Math.min(totalEmailCount, currentOffset + 10).toString(),
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
