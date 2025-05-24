<script lang="ts">
    import { Folder, Mark } from "$lib/types";
    import Icon from "$lib/ui/Components/Icon";
    import * as Context from "$lib/ui/Components/Context";
    import { getCurrentMailbox, type EmailSelection, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
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

    interface Props {
        groupedUidSelection: GroupedUidSelection;
        emailSelection: EmailSelection
        currentOffset: number;
    }

    let {
        groupedUidSelection,
        emailSelection = $bindable(),
        currentOffset,
    }: Props = $props();

    const selectEmail = (selectedEmail: HTMLElement) => {
        if (emailSelection === "1:*") return;
        const selectedEmailCheckbox = selectedEmail.querySelector
            <HTMLInputElement>(".email-preview-selection")!;
        if (!selectedEmailCheckbox.checked) emailSelection = [];
        const selectedEmailUid = selectedEmailCheckbox.value;
        if (!emailSelection.includes(selectedEmailUid)) {
            emailSelection.push(selectedEmailUid);
        }
    };

    const deselectEmail = (lastSelectedEmail: HTMLElement) => {
        if (emailSelection === "1:*") return;
        const lastSelectedEmailCheckbox = lastSelectedEmail.querySelector
            <HTMLInputElement>(".email-preview-selection")!;
        const lastSelectedEmailUid = lastSelectedEmailCheckbox.value;
        emailSelection = emailSelection.filter(
            (selection) => selection !== lastSelectedEmailUid,
        );
    };
</script>

<Context.Root
    selector=".mailbox .email-preview"
    beforeOpen={selectEmail}
    afterClose={deselectEmail}
>
    {#if emailSelection.length > 1 || doAllSelectedEmailsLackMark(emailSelection, Mark.Flagged)}
        <MarkAs
            {groupedUidSelection}
            markType={Mark.Flagged}
            folder={getCurrentMailbox().folder}
        >
            <Icon name="flag" />
            <span>Mark as Important</span>
        </MarkAs>
    {/if}
    {#if emailSelection.length > 1 || doAllSelectedEmailsHaveMark(emailSelection, Mark.Flagged)}
        <MarkAs
            {groupedUidSelection}
            markType={Mark.Flagged}
            folder={getCurrentMailbox().folder}
            isUnmark={true}
        >
            <Icon name="flagged" />
            <span>Unmark as Important</span>
        </MarkAs>
    {/if}
    {#if emailSelection.length > 1 || doAllSelectedEmailsLackMark(emailSelection, Mark.Seen)}
        <MarkAs
            {groupedUidSelection}
            markType={Mark.Seen}
            folder={getCurrentMailbox().folder}
        >
            <Icon name="seen" />
            <span>Mark as seen</span>
        </MarkAs>
    {/if}
    {#if emailSelection.length > 1 || doAllSelectedEmailsHaveMark(emailSelection, Mark.Seen)}
        <MarkAs
            {groupedUidSelection}
            markType={Mark.Seen}
            folder={getCurrentMailbox().folder}
            isUnmark={true}
        >
            <Icon name="unseen" />
            <span>Unmark as seen</span>
        </MarkAs>
    {/if}
    <Context.Separator />
    {#if emailSelection.length == 1}
        <Reply
            {groupedUidSelection}
            {emailSelection}
        >
            <Icon name="reply" />
            <span>Reply</span>
        </Reply>
        <Forward
            {groupedUidSelection}
            {emailSelection}
        >
            <Icon name="forward" />
            <span>Forward</span>
        </Forward>
        <Context.Separator />
        <Unsubscribe
            {groupedUidSelection}
            {emailSelection}
        >
            Unsubscribe
        </Unsubscribe>
    {:else if emailSelection.length > 1}
        {#if doAllSelectedEmailsHaveUnsubscribeOption(groupedUidSelection)}
            <UnsubscribeAll
                {groupedUidSelection}
                {emailSelection}
            >
                Unsubscribe All
            </UnsubscribeAll>
        {/if}
    {/if}
    <Context.Separator />
    {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
        <MoveTo
            {groupedUidSelection}
            sourceFolder={Folder.Archive}
            destinationFolder={Folder.Inbox}
        >
            <Icon name="inbox" />
            <span>Move to Inbox</span>
        </MoveTo>
    {:else}
        <MoveTo
            {groupedUidSelection}
            sourceFolder={getCurrentMailbox().folder}
            destinationFolder={Folder.Archive}
        >
            <Icon name="archive" />
            <span>Archive</span>
        </MoveTo>
    {/if}
    <DeleteFrom
        {groupedUidSelection}
        {currentOffset}
        folder={getCurrentMailbox().folder}
    >
        <Icon name="trash" />
        <span>{isStandardFolder(getCurrentMailbox().folder, Folder.Trash)
            ? "Delete Completely"
            : "Move to Trash"}</span>
    </DeleteFrom>
</Context.Root>
