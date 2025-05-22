<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Account, type Email, Folder, Mark } from "$lib/types";
    import { show as showMessage } from "$lib/ui/Components/Message";

    export function doEmailHaveMark(email: Email, mark: Mark): boolean {
        return (
            !!Object.hasOwn(email, "flags") &&
            !!email.flags &&
            email.flags.includes(mark)
        );
    }

    export function doEmailLackMark(email: Email, mark: Mark): boolean {
        return (
            !!Object.hasOwn(email, "flags") &&
            !!email.flags &&
            !email.flags.includes(mark)
        );
    }

    export function doEmailHaveUnsubscribeOption(email: Email): boolean {
        return !!email.list_unsubscribe;
    }

    export async function fetchUidByMessageId(
        account: Account,
        folder: string | Folder,
        message_id: string
    ): Promise<string | undefined> {
        const searchResult = await MailboxController.searchEmails(
            account,
            folder,
            { message_id: [message_id] },
        );

        if (!searchResult.success || !searchResult.data) {
            showMessage({ title: "new uid could not fetched by message id." });
            console.error(searchResult.message);
            return;
        }

        return searchResult.data[account.email_address][0];
    }
</script>

<script lang="ts">
    import Icon from "$lib/ui/Components/Icon";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { isStandardFolder } from "$lib/utils";
    import MarkAs from "./Operations/MarkAs.svelte";
    import MoveTo from "./Operations/MoveTo.svelte";
    import DeleteFrom from "./Operations/DeleteFrom.svelte";
    import MoveWithSelect from "./Operations/MoveWithSelect.svelte";
    import CopyWithSelect from "./Operations/CopyWithSelect.svelte";
    import Reply from "./Operations/Reply.svelte";
    import Forward from "./Operations/Forward.svelte";
    import Others from "./Operations/Others.svelte";
    import Back from "./Operations/Back.svelte";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let { account, email, currentOffset }: Props = $props();
</script>

<div class="operations">
    <div class="tool-group">
        <Back>
            <Icon name="back" />
        </Back>
    </div>
    <div class="tool-group">
        {#if doEmailLackMark(email, Mark.Flagged)}
            <MarkAs
                {account}
                {email}
                markType={Mark.Flagged}
            >
                <Icon name="star" />
            </MarkAs>
        {:else}
            <MarkAs
                {account}
                {email}
                markType={Mark.Flagged}
                isUnmark={true}
            >
                <Icon name="star" class="filled" />
            </MarkAs>
        {/if}
        {#if doEmailLackMark(email, Mark.Seen)}
            <MarkAs
                {account}
                {email}
                markType={Mark.Seen}
            >
                <Icon name="seen" />
            </MarkAs>
        {:else}
            <MarkAs
                {account}
                {email}
                markType={Mark.Seen}
                isUnmark={true}
            >
                <Icon name="unseen" />
            </MarkAs>
        {/if}
        {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
            <MoveTo
                {account}
                {email}
                sourceFolder={getCurrentMailbox().folder}
                destinationFolder={Folder.Inbox}
            >
                <Icon name="inbox" />
            </MoveTo>
        {:else}
            <MoveTo
                {account}
                {email}
                sourceFolder={getCurrentMailbox().folder}
                destinationFolder={Folder.Archive}
                {currentOffset}
            >
                <Icon name="archive" />
            </MoveTo>
        {/if}
        <DeleteFrom
            {account}
            folder={getCurrentMailbox().folder}
            {email}
            {currentOffset}
        >
            <Icon name="trash" />
        </DeleteFrom>
    </div>
    <div class="tool-group-separator"></div>
    <div class="tool-group">
        <MoveWithSelect
            {account}
            {email}
            {currentOffset}
        />
        <CopyWithSelect
            {account}
            {email}
        />
    </div>
    <div class="tool-group-separator"></div>
    <div class="tool-group">
        <Reply {email}>
            <Icon name="reply" />
        </Reply>
        <Forward {email}>
            <Icon name="forward" />
        </Forward>
    </div>
    <div class="tool-group-separator"></div>
    <div class="tool-group">
        <Others {account} {email} />
    </div>
</div>
