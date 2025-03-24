<script lang="ts">
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
        type Email,
        type OpenMailTaskResults,
    } from "$lib/types";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";

    interface Props {
        isEditingAccount: Account | null;
        isListingAccount: boolean;
    }

    let {
        isEditingAccount = $bindable(),
        isListingAccount = $bindable(),
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
        const response = await MailboxController.init();
        if (!response.success) {
            showMessage({
                content: "Unexpected error while initializing mailboxes.",
            });
            console.error(response.message);
        } else {
            SharedStore.currentAccount = "home";
            SharedStore.currentFolder = Folder.Inbox;
            //await listenForNotifications();
        }
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

            // init recentEmails
            SharedStore.accounts.forEach(account => {
                SharedStore.recentEmails.push({
                    email_address: account.email_address,
                    result: []
                })
            })
        };

        ws.onmessage = (e: MessageEvent) => {
            // Send app notification.
            if (permissionGranted) {
                sendNotification({
                    title: "New Email Received!",
                    body: "Here, look at your new email.",
                });
            }

            (e.data as OpenMailTaskResults<Email[]>).forEach((account) => {
                // Add uid of the email to the recent emails store.
                const currentRecentEmails = SharedStore.recentEmails.find(
                    (current) =>
                        current.email_address === account.email_address,
                );
                if (currentRecentEmails) {
                    currentRecentEmails.result =
                        currentRecentEmails.result.concat(
                            account.result.map((email) => email.uid),
                        );
                }

                // Add email itself to account's mailbox.
                const currentMailbox = SharedStore.mailboxes.find(
                    (current) =>
                        current.email_address === account.email_address,
                );
                if (currentMailbox) {
                    currentMailbox.result.emails =
                        currentMailbox.result.emails.concat(account.result);
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
                                onclick={() => {
                                    isEditingAccount = account;
                                }}
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
                onclick={() => {
                    isListingAccount = false;
                }}
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
