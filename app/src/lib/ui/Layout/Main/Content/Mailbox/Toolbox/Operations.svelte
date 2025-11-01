<script lang="ts" module>
    import type {
        EmailSelection,
        GroupedUidSelection,
        GroupedMessageIdSelection,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { Mark } from "$lib/types";
    import { doEmailHaveMark, doEmailHaveUnsubscribeOption, doEmailLackMark } from "$lib/ui/Layout/Main/Content/Email/Toolbox/Operations.svelte";

    export function doAllSelectedEmailsHaveMark(
        emailSelection: EmailSelection,
        mark: Mark,
    ): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((selection) => {
            const [emailAddress, uid] = selection.split(",");
            return SharedStore.mailboxes[emailAddress].emails.current.find(
                (email: Email) =>
                    email.uid == uid && doEmailHaveMark(email, mark)
            );
        });
    }

    export function doAllSelectedEmailsLackMark(
        emailSelection: EmailSelection,
        mark: Mark,
    ): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((selection) => {
            const [emailAddress, uid] = selection.split(",");
            return SharedStore.mailboxes[emailAddress].emails.current.find(
                (email: Email) =>
                    email.uid == uid && doEmailLackMark(email, mark)
            );
        });
    }

    export function doAllSelectedEmailsHaveUnsubscribeOption(
        groupedUidSelection: GroupedUidSelection,
    ) {
        return groupedUidSelection.every((group) => {
            const emailAddress = group[0];
            const uids = group[1].split(",");
            const targetMailbox =
                SharedStore.mailboxes[emailAddress].emails.current;
            return uids.every((uid) =>
                targetMailbox.find(
                    (email) => email.uid == uid && doEmailHaveUnsubscribeOption(email)
                ),
            );
        });
    }

    export function convertUidSelectionToMessageIds(
        selection: GroupedUidSelection,
    ): GroupedMessageIdSelection {
        let foundSelection: Record<string, string[]> = {};
        selection.map(([email_address, uids]) => {
            foundSelection[email_address] = [];
            uids.split(",").forEach((uid) => {
                const email = SharedStore.mailboxes[
                    email_address
                ].emails.current.find((em) => em.uid === uid);
                if (email) {
                    foundSelection[email_address].push(email.message_id);
                }
            });
            return;
        });
        return Object.entries(foundSelection);
    }

    export async function fetchUidsByMessageIds(
        folder: string,
        selection: GroupedMessageIdSelection,
    ): Promise<GroupedUidSelection> {
        const foundSelection: GroupedUidSelection = [];
        const results = await Promise.allSettled(
            selection.map(async ([email_address, messageIds]) => {
                const response = await MailboxController.searchEmails(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === email_address,
                    )!,
                    folder,
                    { message_id: messageIds },
                );
                if (!response.success || !response.data) {
                    throw new Error(response.message);
                }
                const foundUids = response.data[email_address].join(",");
                foundSelection.push([email_address, foundUids]);
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({ title: "Could not fetched message ids" });
            failed.forEach((f) => console.error(f.reason));
        }

        return foundSelection;
    }
</script>

<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/mailbox";
    import { type Email, Folder } from "$lib/types";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { isStandardFolder } from "$lib/utils";
    import Icon from "$lib/ui/Components/Icon";
    import Refresh from "./Operations/Refresh.svelte";
    import DeleteFrom from "./Operations/DeleteFrom.svelte";
    import MarkAs from "./Operations/MarkAs.svelte";
    import MoveTo from "./Operations/MoveTo.svelte";
    import CopyWithSelect from "./Operations/CopyWithSelect.svelte";
    import MoveWithSelect from "./Operations/MoveWithSelect.svelte";
    import Select from "./Operations/Select.svelte";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";

    const mailboxContext = getMailboxContext();
    let selectedEmails = $derived(mailboxContext.emailSelection.value);
    let selectedEmailCount = $derived(mailboxContext.emailSelection.value.length);
</script>

<div class="operations">
    <div class="tool-group">
        <Select />
    </div>

    {#if selectedEmailCount > 0}
        {@const atLeastOneEmailSelected = selectedEmailCount > 1}
        <div class="tool-group">
            <!-- Standard operations for all accounts -->
            {#if atLeastOneEmailSelected || doAllSelectedEmailsLackMark(selectedEmails, Mark.Flagged)}
                <MarkAs
                    markType={Mark.Flagged}
                    folder={getCurrentMailbox().folder}
                >
                    <Icon name="flag" />
                </MarkAs>
            {/if}
            {#if atLeastOneEmailSelected || doAllSelectedEmailsHaveMark(selectedEmails, Mark.Flagged)}
                <MarkAs
                    markType={Mark.Flagged}
                    folder={getCurrentMailbox().folder}
                    isUnmark={true}
                >
                    <Icon name="flagged"/>
                </MarkAs>
            {/if}
            {#if atLeastOneEmailSelected || doAllSelectedEmailsLackMark(selectedEmails, Mark.Seen)}
                <MarkAs
                    markType={Mark.Seen}
                    folder={getCurrentMailbox().folder}
                >
                    <Icon name="seen" />
                </MarkAs>
            {/if}
            {#if atLeastOneEmailSelected || doAllSelectedEmailsHaveMark(selectedEmails, Mark.Seen)}
                <MarkAs
                    markType={Mark.Seen}
                    folder={getCurrentMailbox().folder}
                    isUnmark={true}
                >
                    <Icon name="unseen" />
                </MarkAs>
            {/if}
            {#if isStandardFolder(getCurrentMailbox().folder, Folder.Archive)}
                <MoveTo
                    sourceFolder={Folder.Archive}
                    destinationFolder={Folder.Inbox}
                >
                    <Icon name="inbox" />
                </MoveTo>
            {:else}
                <MoveTo
                    sourceFolder={getCurrentMailbox().folder}
                    destinationFolder={Folder.Archive}
                >
                    <Icon name="archive" />
                </MoveTo>
            {/if}
            <DeleteFrom
                folder={getCurrentMailbox().folder}
            >
                <Icon name="trash" />
            </DeleteFrom>
        </div>
        <div class="tool-group-separator"></div>
        <div class="tool-group">
            <!-- Account related specific operations -->
            {#if mailboxContext.getGroupedUidSelection().length == 1}
                <CopyWithSelect
                    sourceFolder={getCurrentMailbox().folder}
                />
                <MoveWithSelect
                    sourceFolder={getCurrentMailbox().folder}
                />
            {/if}
        </div>
    {:else}
        <div class="tool-group">
            <Refresh>
                <Icon name="refresh" />
            </Refresh>
        </div>
    {/if}
</div>

<style>
    :global {
        .toolbox {
            & .operations {
                display: flex;
                flex-direction: row;
                align-items: center;
                gap: var(--spacing-sm);
                height: 100%;

                & .tool-group {
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    gap: var(--spacing-md);

                    & .tool {
                        display: flex;
                    }

                    & .dropdown-sm {
                        width: 100px;
                    }
                }

                & .tool-group-separator {
                    height: 75%;
                    margin: 0 var(--spacing-xs);
                    background-color: var(--color-border);
                    width: 1px;
                }
            }
        }
    }
</style>
