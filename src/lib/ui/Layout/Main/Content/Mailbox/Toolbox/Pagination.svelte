<script lang="ts">
    import { getRangePaginationTemplate } from "$lib/templates";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox";
    import {
        paginateMailboxBackward,
        paginateMailboxForward,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";

    const mailboxContext = getMailboxContext();

    const getPreviousEmails = async () => {
        const MAILBOX_LENGTH = Number(PreferencesStore.mailboxLength);
        if (mailboxContext.currentOffset.value <= MAILBOX_LENGTH) return;
        await paginateMailboxBackward(mailboxContext.currentOffset.value);
        mailboxContext.currentOffset.value = Math.min(
            getCurrentMailbox().total,
            mailboxContext.currentOffset.value - MAILBOX_LENGTH,
        );
        mailboxContext.emailSelection.value = [];
    };

    const getNextEmails = async () => {
        if (
            mailboxContext.currentOffset.value >=
            getCurrentMailbox().total
        )
            return;
        await paginateMailboxForward(mailboxContext.currentOffset.value);
        const MAILBOX_LENGTH = Number(PreferencesStore.mailboxLength);
        mailboxContext.currentOffset.value = Math.min(
            getCurrentMailbox().total,
            mailboxContext.currentOffset.value + MAILBOX_LENGTH,
        );
        mailboxContext.emailSelection.value = [];
    };
</script>

<div class="pagination">
    <Button.Action
        type="button"
        class="btn-inline {mailboxContext.currentOffset.value <=
        Number(PreferencesStore.mailboxLength)
            ? 'disabled'
            : ''}"
        onclick={getPreviousEmails}
    >
        <Icon name="prev" />
    </Button.Action>
    <small>
        {getRangePaginationTemplate(
            mailboxContext.currentOffset.value.toString(),
            (
                mailboxContext.currentOffset.value -
                1 +
                Number(PreferencesStore.mailboxLength)
            ).toString(),
            getCurrentMailbox().total.toString(),
        )}
    </small>
    <Button.Action
        type="button"
        class="btn-inline {mailboxContext.currentOffset.value >=
        getCurrentMailbox().total
            ? 'disabled'
            : ''}"
        onclick={getNextEmails}
    >
        <Icon name="next" />
    </Button.Action>
</div>

<style>
    :global {
        .toolbox {
            & .pagination {
                display: flex;
                flex-direction: row;
                align-items: center;
                font-size: var(--font-size-sm);
                gap: var(--spacing-md);
                color: var(--color-text-secondary);

                & svg {
                    width: var(--font-size-md);
                    height: var(--font-size-md);
                }
            }
        }
    }
</style>
