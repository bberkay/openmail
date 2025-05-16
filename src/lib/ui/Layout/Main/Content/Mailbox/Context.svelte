<script lang="ts">
    import { Folder, Mark } from "$lib/types";
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
        groupedUidSelection = $bindable(),
        emailSelection = $bindable(),
        currentOffset = $bindable(),
    }: Props = $props();

    const selectEmail = (e: Event) => {
        if (emailSelection === "1:*") return;
        const selectedEmail = e.target as HTMLElement;
        const selectedEmailUid = selectedEmail.querySelector<HTMLInputElement>(
            ".email-selection-checkbox",
        )!.value;
        emailSelection.push(selectedEmailUid);
    };

    const deselectEmail = (e: Event) => {
        if (emailSelection === "1:*") return;
        const selectedEmail = e.target as HTMLElement;
        const selectedEmailUid = selectedEmail.querySelector<HTMLInputElement>(
            ".email-selection-checkbox",
        )!.value;
        emailSelection = emailSelection.filter(
            (selection) => selection !== selectedEmailUid,
        );
    };
</script>

<Context.Root
    target=".mailbox .email"
    beforeOpen={selectEmail}
    afterClose={deselectEmail}
>
    {#if !doAllSelectedEmailsHaveMark(emailSelection, Mark.Flagged)}
        <MarkAs bind:groupedUidSelection markType={Mark.Flagged}>
            Marked as {Mark.Flagged}
        </MarkAs>
    {/if}
    {#if !doAllSelectedEmailsLackMark(emailSelection, Mark.Flagged)}
        <MarkAs bind:groupedUidSelection markType={Mark.Flagged} isUnmark={true}>
            Unmarked as {Mark.Flagged}
        </MarkAs>
    {/if}
    {#if !doAllSelectedEmailsLackMark(emailSelection, Mark.Seen)}
        <MarkAs bind:groupedUidSelection markType={Mark.Seen}>
            Marked as {Mark.Seen}
        </MarkAs>
    {/if}
    {#if !doAllSelectedEmailsLackMark(emailSelection, Mark.Seen)}
        <MarkAs bind:groupedUidSelection markType={Mark.Seen} isUnmark={true}>
            Unmarked as {Mark.Seen}
        </MarkAs>
    {/if}
    <Context.Separator />
    {#if emailSelection.length == 1}
        <Reply>Reply</Reply>
        <Forward>Forward</Forward>
        <Context.Separator />
        <Unsubscribe>Unsubscribe</Unsubscribe>
    {:else if emailSelection.length > 1}
        {#if doAllSelectedEmailsHaveUnsubscribeOption(groupedUidSelection)}
            <UnsubscribeAll>Unsubscribe All</UnsubscribeAll>
        {/if}
    {/if}
    <Context.Separator />
    {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
        <MoveTo
            bind:groupedUidSelection
            sourceFolder={Folder.Archive}
            destinationFolder={Folder.Inbox}
        >
            Move to Inbox
        </MoveTo>
    {:else}
        <MoveTo
            bind:groupedUidSelection
            sourceFolder={getCurrentMailbox().folder}
            destinationFolder={Folder.Archive}
        >
            Move to Archive
        </MoveTo>
    {/if}
    <DeleteFrom
        bind:currentOffset
        bind:groupedUidSelection
        folder={getCurrentMailbox().folder}
    >
        Delete from {getCurrentMailbox().folder}
    </DeleteFrom>
</Context.Root>
