<script lang="ts">
    import { exit, relaunch } from '@tauri-apps/plugin-process';
    import {
        isPermissionGranted,
        requestPermission,
        sendNotification,
    } from "@tauri-apps/plugin-notification";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        Folder,
        type Account,
    } from "$lib/types";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { isStandardFolder } from '$lib/utils';

    interface Props {
        editAccount: (account: Account) => void
        onCancel: () => void
    }

    let {
        editAccount,
        onCancel,
    }: Props = $props();

    let accountSelection: string[] = $state([]);

    const selectAllAccounts = (event: Event) => {
        const selectAllCheckbox = event.target as HTMLInputElement;
        accountSelection = selectAllCheckbox.checked
            ? SharedStore.failedAccounts
                  .concat(SharedStore.accounts)
                  .map((account) => account.email_address)
            : [];
    };

    const removeAccount = async (e: Event): Promise<void> => {
        showConfirm({
            content: "Are you certain? Deleting an account cannot be undone.",
            onConfirmText: "Yes, remove.",
            onConfirm: async (e: Event) => {
                const target = e.target as HTMLButtonElement;
                const account = target.getAttribute("data-email-address")!;
                const response = await AccountController.remove(account);

                if (!response.success) {
                    showMessage({
                        content: "Unexpected error while removing account.",
                    });
                    console.error(response.message);
                }
            },
        });
    };

    const removeAllAccounts = async (): Promise<void> => {
        showConfirm({
            content: "Are you certain? You are about to remove all accounts.",
            onConfirmText: "Yes, remove all.",
            onConfirm: async (e: Event) => {
                const response = await AccountController.removeAll();

                if (!response.success) {
                    showMessage({
                        content: "Unexpected error while removing accounts.",
                    });
                    console.error(response.message);
                }
            },
        });
    };

    async function initMailboxes(): Promise<void> {
        SharedStore.currentAccount = "home";
        const response = await MailboxController.init();
        if (!response.success) {
            console.error(response.message);
            showConfirm({
                content: "Unexpected error while initializing mailboxes.",
                onConfirmText: "Restart",
                onConfirm: async () => { await relaunch() },
                onCancelText: "Exit",
                onCancel: async () => { await exit(1) },
            });
            return;
        }
        //await listenForNotifications();
    }

    /**
     * Create WebSocket connections
     * for every account to receive
     * new email notifications.
     */
    async function listenForNotifications() {
        const ws = new WebSocket(
            SharedStore.server.replace("http", "ws") +
                `/notifications/${SharedStore.accounts.map((acc) => acc.email_address).join(",")}`,
        );

        let permissionGranted = false;
        ws.onopen = async () => {
            permissionGranted = await isPermissionGranted();
            if (!permissionGranted) {
                const permission = await requestPermission();
                permissionGranted = permission === "granted";
            }

            SharedStore.accounts.forEach((account) => {
                SharedStore.recentEmails[account.email_address] = [];
            });
        };

        ws.onmessage = (e: MessageEvent) => {
            // Send app notification.
            if (permissionGranted) {
                sendNotification({
                    title: "New Email Received!",
                    body: "Here, look at your new email.",
                });
            }

            Object.entries(e.data as typeof SharedStore.recentEmails).forEach((entry) => {
                const emailAddr = entry[0];
                const recentEmails = entry[1];

                // Add email to mailbox
                if (Object.hasOwn(SharedStore.mailboxes, emailAddr)
                    && isStandardFolder(SharedStore.mailboxes[emailAddr].folder, Folder.Inbox)) {
                    const recentEmailsLength = recentEmails.length;
                    SharedStore.mailboxes[emailAddr].emails.current.unshift(...recentEmails);
                    const overflowEmails = SharedStore.mailboxes[emailAddr].emails.current.splice(-1 * recentEmailsLength);
                    SharedStore.mailboxes[emailAddr].emails.next.unshift(...overflowEmails);
                    SharedStore.mailboxes[emailAddr].emails.next.splice(-1 * recentEmailsLength, recentEmailsLength);
                }

                // and recent emails.
                if (Object.hasOwn(SharedStore.recentEmails, emailAddr)) {
                    SharedStore.recentEmails[emailAddr].push(...recentEmails);
                }
            });
        };

        ws.onclose = (e: CloseEvent) => {
            if (e.reason && e.reason.toLowerCase().includes("error")) {
                console.error(e.reason);
            }
        };
    }

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("alert-container", {
                content: `There were ${SharedStore.failedAccounts.length} accounts that failed to connect.`,
                type: "error",
            });
        }
    });
</script>

<div>
    <div class="alert-container" style="margin-bottom:15px;"></div>
    {#if (SharedStore.accounts && SharedStore.accounts.length > 0) || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)}
        {@const failedAccountLength = (SharedStore.failedAccounts || []).length}
        <Table.Root>
            <Table.Header>
                <Table.Row>
                    <Table.Head class="checkbox-cell">
                        <Input.Basic
                            type="checkbox"
                            onclick={selectAllAccounts}
                        />
                    </Table.Head>
                    <Table.Head class="body-cell">
                        Account{accountSelection.length > 0
                            ? ` (${accountSelection.length} selected)`
                            : ""}
                    </Table.Head>
                    <Table.Head>
                        {#if accountSelection.length > 0}
                            <Button.Action
                                class="btn-inline"
                                onclick={removeAllAccounts}
                            >
                                Remove All
                            </Button.Action>
                        {:else}
                            <Button.Action
                                class="btn-inline invisible"
                                onclick={() => {}}
                            >
                                invisible
                            </Button.Action>
                        {/if}
                    </Table.Head>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {#each SharedStore.failedAccounts.concat(SharedStore.accounts) as account, index}
                    <Table.Row
                        class={index < failedAccountLength ? "failed" : ""}
                    >
                        <Table.Cell class="checkbox-cell">
                            <Input.Basic
                                type="checkbox"
                                bind:group={accountSelection}
                                value={account.email_address}
                            />
                        </Table.Cell>
                        <Table.Cell class="body-cell">
                            {index < failedAccountLength ? "Warning" : ""}
                            {account.fullname} &lt;{account.email_address}&gt;
                        </Table.Cell>
                        <Table.Cell class="action-cell">
                            <Button.Basic
                                type="button"
                                class="btn-inline"
                                style="margin-right: 5px;"
                                onclick={() => { editAccount(account) }}
                            >
                                Edit
                            </Button.Basic>
                            <Button.Action
                                class="btn-inline"
                                onclick={removeAccount}
                                data-email-address={account.email_address}
                            >
                                Remove
                            </Button.Action>
                        </Table.Cell>
                    </Table.Row>
                {/each}
            </Table.Body>
        </Table.Root>

        <div class="landing-body-footer">
            {#if failedAccountLength === 0}
                <Button.Action
                    onclick={initMailboxes}
                    disabled={!SharedStore.accounts ||
                        SharedStore.accounts.length == 0}
                >
                    Continue to mailbox.
                </Button.Action>
            {/if}

            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={onCancel}
            >
                I want to add another account.
            </Button.Basic>
        </div>
    {/if}
</div>

<style>
    :global {
        .checkbox-cell {
            width: var(--font-size-2xl);
            padding-left: var(--spacing-xs) !important;
            padding-bottom: 0 !important;
        }

        .body-cell {
            padding-left: var(--spacing-xs);
            padding-top: var(--spacing-md);
            text-align: left;
        }

        .action-cell {
            padding-right: var(--spacing-2xs);
            white-space: nowrap;
            width: calc(2 * var(--font-size-2xl));
            text-align: right;
        }
    }
</style>
