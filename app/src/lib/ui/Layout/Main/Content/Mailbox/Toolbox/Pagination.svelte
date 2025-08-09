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
    import { PreferenceStore } from "$lib/preferences";

    const mailboxContext = getMailboxContext();

    let currentEmailLength = $derived(getCurrentMailbox().emails.current.length);

    let pageInfo = $derived(getRangePaginationTemplate(
        mailboxContext.currentOffset.value.toString(),
        (
            mailboxContext.currentOffset.value -
            1 + currentEmailLength
        ).toString(),
        getCurrentMailbox().total.toString(),
    ));

    let isPrevBtnDisabled = $derived(
        mailboxContext.currentOffset.value <= currentEmailLength
    );

    let isNextBtnDisabled = $derived(
        mailboxContext.currentOffset.value >= getCurrentMailbox().total
    );

    const getPreviousEmails = async () => {
        if (mailboxContext.currentOffset.value <= currentEmailLength) return;
        await paginateMailboxBackward(mailboxContext.currentOffset.value);
        mailboxContext.currentOffset.value = Math.min(
            getCurrentMailbox().total,
            mailboxContext.currentOffset.value - currentEmailLength,
        );
        mailboxContext.emailSelection.value = [];
    };

    const getNextEmails = async () => {
        if (
            mailboxContext.currentOffset.value >=
            getCurrentMailbox().total
        )
            return;
        // TODO: Convert this to the paginateEmails.
        // TODO: Also why doesnt emails.next comes as empty list, fetch next
        // emails as soon as app starts.
        await paginateMailboxForward(mailboxContext.currentOffset.value);
        mailboxContext.currentOffset.value = Math.min(
            getCurrentMailbox().total,
            mailboxContext.currentOffset.value + currentEmailLength,
        );
        mailboxContext.emailSelection.value = [];
    };
</script>

<div class="pagination">
    <Button.Action
        type="button"
        class="btn-inline {isPrevBtnDisabled ? 'disabled' : ''}"
        onclick={getPreviousEmails}
    >
        <Icon name="prev" />
    </Button.Action>
    <small>
        {pageInfo}
    </small>
    <Button.Action
        type="button"
        class="btn-inline {isNextBtnDisabled ? 'disabled' : ''}"
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
