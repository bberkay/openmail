<script lang="ts">
    import { getRangePaginationTemplate } from "$lib/templates";
    import {
        getCurrentMailbox,
        paginateMailboxBackward,
        paginateMailboxForward,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { SharedStore } from "$lib/stores/shared.svelte";

    interface Props {
        currentOffset: number;
    }

    let { currentOffset = $bindable() }: Props = $props();

    const getPreviousEmails = async () => {
        const MAILBOX_LENGTH = SharedStore.preferences.mailboxLength;
        if (currentOffset <= MAILBOX_LENGTH) return;
        await paginateMailboxBackward(currentOffset);
        currentOffset = Math.min(
            getCurrentMailbox().total,
            currentOffset + MAILBOX_LENGTH,
        );
    };

    const getNextEmails = async () => {
        if (currentOffset >= getCurrentMailbox().total) return;
        await paginateMailboxForward(currentOffset);
        const MAILBOX_LENGTH = SharedStore.preferences.mailboxLength;
        currentOffset = Math.min(
            getCurrentMailbox().total,
            currentOffset + MAILBOX_LENGTH,
        );
    };
</script>

<div class="toolbox-right">
    <div class="pagination">
        <Button.Action
            type="button"
            class="btn-inline {currentOffset <= SharedStore.preferences.mailboxLength
                ? 'disabled'
                : ''}"
            onclick={getPreviousEmails}
        >
            {local.prev[DEFAULT_LANGUAGE]}
        </Button.Action>
        <small>
            {getRangePaginationTemplate(
                currentOffset.toString(),
                (currentOffset - 1 + SharedStore.preferences.mailboxLength).toString(),
                getCurrentMailbox().total.toString(),
            )}
        </small>
        <Button.Action
            type="button"
            class="btn-inline {currentOffset >= getCurrentMailbox().total
                ? 'disabled'
                : ''}"
            onclick={getNextEmails}
        >
            {local.next[DEFAULT_LANGUAGE]}
        </Button.Action>
    </div>
</div>
