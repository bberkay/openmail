<script lang="ts">
    import { Folder, Mark } from "$lib/types";
    import Icon from "$lib/ui/Components/Icon";
    import * as Context from "$lib/ui/Components/Context";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { isStandardFolder } from "$lib/utils";
    import Forward from "./Context/Forward.svelte";
    import Reply from "./Context/Reply.svelte";
    import MarkAs from "./Context/MarkAs.svelte";
    import MoveTo from "./Context/MoveTo.svelte";
    import {
        doAllSelectedEmailsHaveMark,
        doAllSelectedEmailsLackMark,
        doAllSelectedEmailsHaveUnsubscribeOption,
    } from "./Toolbox/Operations.svelte";
    import DeleteFrom from "./Context/DeleteFrom.svelte";
    import Unsubscribe from "./Context/Unsubscribe.svelte";
    import UnsubscribeAll from "./Context/UnsubscribeAll.svelte";

    const mailboxContext = getMailboxContext();

    const selectEmail = (selectedEmail: HTMLElement) => {
        if (mailboxContext.emailSelection.value === "1:*") return;
        const selectedEmailCheckbox =
            selectedEmail.querySelector<HTMLInputElement>(
                ".email-preview-selection",
            )!;
        if (!selectedEmailCheckbox.checked)
            mailboxContext.emailSelection.value = [];
        const selectedEmailUid = selectedEmailCheckbox.value;
        if (!mailboxContext.emailSelection.value.includes(selectedEmailUid)) {
            mailboxContext.emailSelection.value.push(selectedEmailUid);
        }
    };

    const deselectEmail = (lastSelectedEmail: HTMLElement) => {
        if (mailboxContext.emailSelection.value === "1:*") return;
        const lastSelectedEmailCheckbox =
            lastSelectedEmail.querySelector<HTMLInputElement>(
                ".email-preview-selection",
            )!;
        const lastSelectedEmailUid = lastSelectedEmailCheckbox.value;
        mailboxContext.emailSelection.value =
            mailboxContext.emailSelection.value.filter(
                (selection) => selection !== lastSelectedEmailUid,
            );
    };
</script>

<Context.Root
    selector=".mailbox .email-preview"
    beforeOpen={selectEmail}
    afterClose={deselectEmail}
>
    {#if mailboxContext.emailSelection.value.length > 1 || doAllSelectedEmailsLackMark(mailboxContext.emailSelection.value, Mark.Flagged)}
        <MarkAs
            markType={Mark.Flagged}
            folder={mailboxContext.getCurrentMailbox().folder}
        >
            <Icon name="flag" />
            <span>Mark as Important</span>
        </MarkAs>
    {/if}
    {#if mailboxContext.emailSelection.value.length > 1 || doAllSelectedEmailsHaveMark(mailboxContext.emailSelection.value, Mark.Flagged)}
        <MarkAs
            markType={Mark.Flagged}
            folder={mailboxContext.getCurrentMailbox().folder}
            isUnmark={true}
        >
            <Icon name="flagged" />
            <span>Unmark as Important</span>
        </MarkAs>
    {/if}
    {#if mailboxContext.emailSelection.value.length > 1 || doAllSelectedEmailsLackMark(mailboxContext.emailSelection.value, Mark.Seen)}
        <MarkAs
            markType={Mark.Seen}
            folder={mailboxContext.getCurrentMailbox().folder}
        >
            <Icon name="seen" />
            <span>Mark as seen</span>
        </MarkAs>
    {/if}
    {#if mailboxContext.emailSelection.value.length > 1 || doAllSelectedEmailsHaveMark(mailboxContext.emailSelection.value, Mark.Seen)}
        <MarkAs
            markType={Mark.Seen}
            folder={mailboxContext.getCurrentMailbox().folder}
            isUnmark={true}
        >
            <Icon name="unseen" />
            <span>Unmark as seen</span>
        </MarkAs>
    {/if}
    <Context.Separator />
    {#if mailboxContext.emailSelection.value.length == 1}
        <Reply>
            <Icon name="reply" />
            <span>Reply</span>
        </Reply>
        <Forward>
            <Icon name="forward" />
            <span>Forward</span>
        </Forward>
        <Context.Separator />
        <Unsubscribe>Unsubscribe</Unsubscribe>
    {:else if mailboxContext.emailSelection.value.length > 1}
        {#if doAllSelectedEmailsHaveUnsubscribeOption(mailboxContext.getGroupedUidSelection())}
            <UnsubscribeAll>Unsubscribe All</UnsubscribeAll>
        {/if}
    {/if}
    <Context.Separator />
    {#if isStandardFolder(mailboxContext.getCurrentMailbox().folder, Folder.Archive)}
        <MoveTo sourceFolder={Folder.Archive} destinationFolder={Folder.Inbox}>
            <Icon name="inbox" />
            <span>Move to Inbox</span>
        </MoveTo>
    {:else}
        <MoveTo
            sourceFolder={mailboxContext.getCurrentMailbox().folder}
            destinationFolder={Folder.Archive}
        >
            <Icon name="archive" />
            <span>Archive</span>
        </MoveTo>
    {/if}
    <DeleteFrom folder={mailboxContext.getCurrentMailbox().folder}>
        <Icon name="trash" />
        <span>
            {isStandardFolder(
                mailboxContext.getCurrentMailbox().folder,
                Folder.Trash,
            )
                ? "Delete Completely"
                : "Move to Trash"}
        </span>
    </DeleteFrom>
</Context.Root>
