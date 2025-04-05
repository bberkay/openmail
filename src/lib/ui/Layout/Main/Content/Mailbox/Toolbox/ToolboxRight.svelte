<script lang="ts">
    import { MAILBOX_LENGTH } from "$lib/controllers/MailboxController";
    import { MAILBOX_PAGINATION_TEMPLATE } from "$lib/constants";
    import {
        getCurrentMailbox,
        paginateMailboxBackward,
        paginateMailboxForward,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Button from "$lib/ui/Components/Button";

    let currentOffset = $state(1);

    const getPreviousEmails = async () => {
        if (currentOffset <= MAILBOX_LENGTH) return;
        currentOffset = await paginateMailboxBackward(currentOffset);
    };

    const getNextEmails = async () => {
        if (currentOffset >= getCurrentMailbox().total) return;
        currentOffset = await paginateMailboxForward(currentOffset);
    };
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset <= MAILBOX_LENGTH
                ? 'disabled'
                : ''}"
            onclick={getPreviousEmails}
        >
            Prev
        </Button.Action>
        <small>
            {MAILBOX_PAGINATION_TEMPLATE.replace(
                "{offset_start}",
                currentOffset.toString(),
            )
                .replace(
                    "{offset_end}",
                    (currentOffset - 1 + MAILBOX_LENGTH).toString(),
                )
                .replace("{total}", getCurrentMailbox().total.toString())
                .trim()}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= getCurrentMailbox().total
                ? 'disabled'
                : ''}"
            onclick={getNextEmails}
        >
            Next
        </Button.Action>
    </div>
</div>
