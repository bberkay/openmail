<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { type Email, Mark, Folder, type Account } from "$lib/types";
    import { startsWithAnyOf } from "$lib/utils";
    import * as Select from "$lib/ui/Components/Select";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";

    interface Props {
        emailSelection: "1:*" | string[];
    }

    let { emailSelection = $bindable([]) }: Props = $props();

    let groupedEmailSelection: [string, string][] = $state([]);

    let isMailboxOfCustomFolder = $derived.by(() => {
        if (SharedStore.currentAccount == "home") return false;
        return !startsWithAnyOf(
            SharedStore.currentMailbox.folder,
            Object.values(Folder),
        );
    });

    let customFoldersOfSelection = $derived.by(() => {
        if (
            !(
                SharedStore.currentAccount !== "home" ||
                groupedEmailSelection.length < 2
            )
        )
            return [];

        const currentEmailAddr =
            SharedStore.currentAccount !== "home"
                ? SharedStore.currentAccount.email_address
                : groupedEmailSelection[0][0];
        return SharedStore.customFolders.find(
            (acc) => acc.email_address === currentEmailAddr,
        )!.result;
    });

    let selectShownCheckbox: HTMLInputElement;
    let shownEmailUids: string[] = $state([]);
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    function groupEmailSelectionByAccount() {
        const accountUidMap: Record<string, string> = {};
        if (emailSelection === "1:*") {
            SharedStore.accounts.forEach((account) => {
                if (["home", account].includes(SharedStore.currentAccount)) {
                    accountUidMap[account.email_address] = "1:*";
                }
            });
        } else {
            emailSelection.forEach((selection) => {
                const [emailAddr, uid] = selection.split(",");
                if (!Object.hasOwn(accountUidMap, emailAddr)) {
                    accountUidMap[emailAddr] = uid;
                } else {
                    accountUidMap[emailAddr] = accountUidMap[emailAddr].concat(
                        ",",
                        uid,
                    );
                }
            });
        }
        return accountUidMap;
    }

    $effect(() => {
        if (SharedStore.currentMailbox) {
            document
                .querySelectorAll<HTMLInputElement>(
                    ".mailbox .email-selection-checkbox",
                )
                .forEach((element) => {
                    shownEmailUids.push(element.value);
                });
        }

        if (emailSelection) {
            groupedEmailSelection = Object.entries(
                groupEmailSelectionByAccount(),
            );
        }
    });

    const selectShownEmails = (event: Event) => {
        emailSelection = selectShownCheckbox.checked ? shownEmailUids : [];
    };

    function isSelectedEmailsIncludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((uid) => {
            return SharedStore.currentMailbox.emails.find(
                (email: Email) =>
                    email.uid == uid &&
                    Object.hasOwn(email, "flags") &&
                    email.flags!.includes(mark),
            );
        });
    }

    function isSelectedEmailsExcludesGivenMark(mark: Mark): boolean {
        if (emailSelection === "1:*") return false;

        return emailSelection.every((uid) => {
            return SharedStore.currentMailbox.emails.find(
                (email: Email) =>
                    email.uid == uid &&
                    Object.hasOwn(email, "flags") &&
                    !email.flags!.includes(mark),
            );
        });
    }

    async function markEmails(mark: string | Mark) {
        groupedEmailSelection.forEach(async (group) => {
            const response = await MailboxController.markEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === group[0],
                )!,
                group[1],
                mark,
                SharedStore.currentFolder,
            );
            if (!response.success) {
                showMessage({
                    content: `Unexpected error while marking email as ${mark}`,
                });
                console.error(response.message);
            }
        });
    }

    async function unmarkEmails(mark: string | Mark) {
        groupedEmailSelection.forEach(async (group) => {
            const response = await MailboxController.unmarkEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === group[0],
                )!,
                group[1],
                mark,
                SharedStore.currentFolder,
            );
            if (!response.success) {
                showMessage({
                    content: `Unexpected error while marking email as ${mark}`,
                });
                console.error(response.message);
            }
        });
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
            SharedStore.currentAccount !== "home"
                ? SharedStore.currentAccount
                : SharedStore.accounts.find(
                      (acc) =>
                          acc.email_address === groupedEmailSelection[0][0],
                  )!,
            groupedEmailSelection[0][1],
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
            SharedStore.currentAccount !== "home"
                ? SharedStore.currentAccount
                : SharedStore.accounts.find(
                      (acc) =>
                          acc.email_address === groupedEmailSelection[0][0],
                  )!,
            groupedEmailSelection[0][1],
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
        groupedEmailSelection.forEach(async (group) => {
            const response = await MailboxController.moveEmails(
                SharedStore.accounts.find(
                    (acc) => acc.email_address === group[0],
                )!,
                group[1],
                SharedStore.currentFolder,
                Folder.Archive,
            );

            if (!response.success) {
                showMessage({
                    content: "Unexpected error while moving email.",
                });
                console.error(response.message);
                return;
            }
        });
    };

    const deleteFrom = async (): Promise<void> => {
        showConfirm({
            content: "Are you certain? Deleting an email cannot be undone.",
            onConfirmText: "Yes, delete.",
            onConfirm: async (e: Event) => {
                groupedEmailSelection.forEach(async (group) => {
                    const response = await MailboxController.deleteEmails(
                        SharedStore.accounts.find(
                            (acc) => acc.email_address === group[0],
                        )!,
                        group[1],
                        SharedStore.currentFolder,
                    );
                    if (!response.success) {
                        showMessage({
                            content: "Unexpected error while deleting email.",
                        });
                        console.error(response.message);
                    }
                });
            },
        });
    };

    const refresh = async (): Promise<void> => {
        const response = await MailboxController.getMailboxes(
            SharedStore.currentAccount === "home"
                ? SharedStore.accounts
                : SharedStore.currentAccount,
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
        {#if groupedEmailSelection.length < 2}
            <div class="tool-separator"></div>
            <div class="tool">
                {#if customFoldersOfSelection}
                    <Select.Root onchange={copyTo} placeholder="Copy To">
                        {#if isMailboxOfCustomFolder}
                            <!-- Add inbox option if email is in custom folder -->
                            <Select.Option value={Folder.Inbox}>
                                {Folder.Inbox}
                            </Select.Option>
                        {/if}
                        {#each customFoldersOfSelection as customFolder}
                            {#if SharedStore.currentAccount === "home" || customFolder !== SharedStore.currentMailbox.folder}
                                <Select.Option value={customFolder}>
                                    {customFolder}
                                </Select.Option>
                            {/if}
                        {/each}
                    </Select.Root>
                {/if}
            </div>
            <div class="tool">
                {#if customFoldersOfSelection}
                    <Select.Root onchange={moveTo} placeholder="Move To">
                        {#if isMailboxOfCustomFolder}
                            <!-- Add inbox option if email is in custom folder -->
                            <Select.Option value={Folder.Inbox}>
                                {Folder.Inbox}
                            </Select.Option>
                        {/if}
                        {#each customFoldersOfSelection as customFolder}
                            {#if SharedStore.currentAccount === "home" || customFolder !== SharedStore.currentMailbox.folder}
                                <Select.Option value={customFolder}>
                                    {customFolder}
                                </Select.Option>
                            {/if}
                        {/each}
                    </Select.Root>
                {/if}
            </div>
        {/if}
    {:else}
        <div class="tool">
            <Button.Action type="button" class="btn-inline" onclick={refresh}>
                Refresh
            </Button.Action>
        </div>
    {/if}
</div>
