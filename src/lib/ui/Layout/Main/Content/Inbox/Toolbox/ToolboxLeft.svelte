<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email, Mark, Folder } from "$lib/types";
    import { startsWithAnyOf } from "$lib/utils";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";

    interface Props {
        emailSelection: string[];
    }

    let { emailSelection = $bindable([]) }: Props = $props();

    let isAllEmailsSelected = $state(false);

    let customFoldersOfAccount = $derived(
        SharedStore.currentAccount
            ? SharedStore.customFolders.find(
                  (acc) =>
                      acc.email_address ===
                      SharedStore.currentAccount!.email_address,
              )!.result
            : [],
    );
    let isMailboxOfCustomFolder = $derived(
        !startsWithAnyOf(currentMailbox.folder, Object.values(Folder)),
    );

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    const selectShownEmails = (event: Event) => {
        emailSelection = selectShownCheckbox.checked
            ? currentMailbox.emails.map((email: Email) => email.uid).flat()
            : [];
    };

    function isSelectedEmailsIncludesGivenMark(mark: Mark): boolean {
        if (isAllEmailsSelected) {
            return currentMailbox.emails.every(
                (email: Email) =>
                    Object.hasOwn(email, "flags") &&
                    email.flags!.includes(mark),
            );
        } else {
            return emailSelection.every((uid) => {
                return currentMailbox.emails.find(
                    (email: Email) =>
                        email.uid == uid &&
                        Object.hasOwn(email, "flags") &&
                        email.flags!.includes(mark),
                );
            });
        }
    }

    function isSelectedEmailsExcludesGivenMark(mark: Mark): boolean {
        if (isAllEmailsSelected) {
            return currentMailbox.emails.every(
                (email: Email) =>
                    Object.hasOwn(email, "flags") &&
                    !email.flags!.includes(mark),
            );
        } else {
            return emailSelection.every((uid) => {
                return currentMailbox.emails.find(
                    (email: Email) =>
                        email.uid == uid &&
                        Object.hasOwn(email, "flags") &&
                        !email.flags!.includes(mark),
                );
            });
        }
    }

    async function markEmails(mark: string | Mark) {
        const response = await MailboxController.markEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder,
        );
        if (!response.success) {
            showMessage({
                content: `Unexpected error while marking email as ${mark}`,
            });
            console.error(response.message);
        }
    }

    async function unmarkEmails(mark: string | Mark) {
        const response = await MailboxController.unmarkEmails(
            SharedStore.currentAccount,
            emailSelection,
            mark,
            SharedStore.currentFolder,
        );
        if (!response.success) {
            showMessage({
                content: `Unexpected error while marking email as ${mark}`,
            });
            console.error(response.message);
        }
    }

    const markAsRead = async (): Promise<void> => {
        await markEmails(Mark.Seen);
    };

    const markAsUnread = async (): Promise<void> => {
        await unmarkEmails(Mark.Seen);
    };

    const markAsImportant = async (): Promise<void> => {
        await markEmails(Mark.Flagged);
    };

    const markAsNotImportant = async (): Promise<void> => {
        await unmarkEmails(Mark.Flagged);
    };

    const copyTo = async (
        destinationFolder: string | Folder,
    ): Promise<void> => {
        const response = await MailboxController.copyEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({ content: "Unexpected error while copying email." });
            console.error(response.message);
        }
    };

    const moveTo = async (
        destinationFolder: string | Folder,
    ): Promise<void> => {
        const response = await MailboxController.moveEmails(
            SharedStore.currentAccount,
            emailSelection,
            SharedStore.currentFolder,
            destinationFolder,
        );

        if (!response.success) {
            showMessage({ content: "Unexpected error while moving email." });
            console.error(response.message);
            return;
        }
    };

    const moveToArchive = async (): Promise<void> => {
        moveTo(Folder.Archive);
    };

    const deleteFrom = async (): Promise<void> => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                const response = await MailboxController.deleteEmails(
                    SharedStore.currentAccount,
                    emailSelection,
                    SharedStore.currentFolder,
                );
                if (!response.success) {
                    showMessage({
                        content: "Unexpected error while deleting email.",
                    });
                    console.error(response.message);
                }
            },
        });
    };

    const refresh = async (): Promise<void> => {
        const response = await MailboxController.getMailboxes(
            SharedStore.currentAccount === "home"
                ? SharedStore.accounts
                : SharedStore.currentAccount
        );
        if (!response.success) {
            showMessage({ content: "Error while refreshing mailboxes." });
            console.error(response.message);
        }
    };
</script>

<div class="toolbox-left">
    <div class="tool">
        <Input.Basic
            type="checkbox"
            id="select-shown"
            onclick={selectShownEmails}
        />
    </div>
    {#if emailSelection.length > 0}
        {#if !isSelectedEmailsIncludesGivenMark(Mark.Flagged)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={markAsImportant}
                >
                    Star
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsExcludesGivenMark(Mark.Flagged)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={markAsNotImportant}
                >
                    Remove Star
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsIncludesGivenMark(Mark.Seen)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={markAsRead}
                >
                    Mark as Read
                </Button.Action>
            </div>
        {/if}
        {#if !isSelectedEmailsExcludesGivenMark(Mark.Seen)}
            <div class="tool">
                <Button.Action
                    type="button"
                    class="btn-inline"
                    onclick={markAsUnread}
                >
                    Mark as Unread
                </Button.Action>
            </div>
        {/if}
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={moveToArchive}
            >
                Archive
            </Button.Action>
        </div>
        <div class="tool">
            <Button.Action
                type="button"
                class="btn-inline"
                onclick={deleteFrom}
            >
                Delete
            </Button.Action>
        </div>
        <div class="tool-separator"></div>
        <div class="tool">
            {#if customFoldersOfAccount}
                <Select.Root onchange={copyTo} placeholder="Copy To">
                    {#each customFoldersOfAccount as customFolder}
                        {#if customFolder !== currentMailbox.folder}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                    {#if isMailboxOfCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                </Select.Root>
            {/if}
        </div>
        <div class="tool">
            {#if customFoldersOfAccount}
                <Select.Root onchange={moveTo} placeholder="Move To">
                    {#each customFoldersOfAccount as customFolder}
                        {#if customFolder !== currentMailbox.folder}
                            <Select.Option value={customFolder}>
                                {customFolder}
                            </Select.Option>
                        {/if}
                    {/each}
                    {#if isMailboxOfCustomFolder}
                        <!-- Add inbox option if email is in custom folder -->
                        <Select.Option value={Folder.Inbox}>
                            {Folder.Inbox}
                        </Select.Option>
                    {/if}
                </Select.Root>
            {/if}
        </div>
    {:else}
        <div class="tool">
            <Button.Action type="button" class="btn-inline" onclick={refresh}>
                Refresh
            </Button.Action>
        </div>
    {/if}
</div>
