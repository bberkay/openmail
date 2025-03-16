<script lang="ts">
    import {
      isPermissionGranted,
      requestPermission,
      sendNotification,
    } from '@tauri-apps/plugin-notification';
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account, type Email, type OpenMailTaskResults } from "$lib/types";
    import * as Button from "$lib/ui/Elements/Button";
    import * as Input from "$lib/ui/Elements/Input";
    import * as Table from "$lib/ui/Elements/Table";
    import { show as showAlert } from "$lib/ui/Elements/Alert";

    const accountController = new AccountController();
    const mailboxController = new MailboxController();

    interface Props {
        isEditingAccount: Account | null;
        isListingAccount: boolean;
    }

    let {
        isEditingAccount = $bindable(),
        isListingAccount = $bindable()
    }: Props = $props();
    let accountSelection: string[] = $state([]);

    const removeAccount = async (e: Event): Promise<void> => {
        if (confirm("Are you certain? Deleting an account cannot be undone.")) {
            const target = e.target as HTMLButtonElement;
            const account = target.getAttribute("data-email-address")!;
            const response = await accountController.remove(account);

            if (!response.success) {
                alert(response.message);
            }
        }
    };

    const removeAllAccounts = async (): Promise<void> => {
        if (confirm("Are you certain? You are about to remove all accounts.")) {
            const response = await accountController.removeAll();

            if (!response.success) {
                alert(response.message);
            }
        }
    };

    const selectAllAccounts = (event: Event) => {
        const selectAllCheckbox = event.target as HTMLInputElement;
        accountSelection = selectAllCheckbox.checked
            ? SharedStore.failedAccounts.concat(SharedStore.accounts).map((account) => account.email_address)
            : [];
    }

    async function initMailboxes(): Promise<void> {
        const response = await mailboxController.init();
        if (!response.success) {
            alert(response.message);
        } else {
            SharedStore.currentAccount = null;
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
            `/notifications/${SharedStore.accounts.map(acc => acc.email_address).join(",")}`
        );

        let permissionGranted = false;
        ws.onopen = async () => {
            permissionGranted = await isPermissionGranted();
            if (!permissionGranted) {
              const permission = await requestPermission();
              permissionGranted = permission === 'granted';
            }
        }

        ws.onmessage = (e: MessageEvent) => {
            // Send app notification.
            if (permissionGranted) {
                sendNotification({
                    title: 'New Email Received!',
                    body: 'Here, look at your new email.'
                });
            }

            (e.data as OpenMailTaskResults<Email[]>).forEach((account) => {
                // Add uid of the email to the recent emails store.
                const currentRecentEmails = SharedStore.recentEmails.find(
                    current => current.email_address === account.email_address
                );
                if (currentRecentEmails) {
                    currentRecentEmails.result = currentRecentEmails.result.concat(
                        account.result.map(email => email.uid)
                    );
                }

                // Add email itself to account's mailbox.
                const currentMailbox = SharedStore.mailboxes.find(
                    current => current.email_address === account.email_address
                );
                if (currentMailbox) {
                    currentMailbox.result.emails = currentMailbox.result.emails.concat(account.result);
                }
            })
        }

        ws.onclose = (e: CloseEvent) => {
            if(e.reason && e.reason.toLowerCase().includes("error")) {
                alert(e.reason);
            }
        }
    }

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert(
                "alert-container",
                `There were ${SharedStore.failedAccounts.length} accounts that failed to
                connect.`,
                "error"
            );
        }
    });
</script>

<div>
    <div class="alert-container" style="margin-bottom:15px;"></div>
    {#if
        (SharedStore.accounts && SharedStore.accounts.length > 0)
        || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)
    }
        {@const failedAccountLength = (SharedStore.failedAccounts || []).length}
        <Table.Root>
            <Table.Header>
                <Table.Row>
                    <Table.Head>
                        <Input.Basic
                            type="checkbox"
                            onclick={selectAllAccounts}
                        />
                    </Table.Head>
                    <Table.Head>
                        Account{accountSelection.length > 0 ? ` (${accountSelection.length} selected)` : ""}
                    </Table.Head>
                    <Table.Head colspan="2">
                        {#if accountSelection.length > 0}
                            <Button.Action
                                class="inline"
                                onclick={removeAllAccounts}
                            >
                                Remove All
                            </Button.Action>
                        {:else}
                            <Button.Action
                                class="inline"
                                style="visibility: hidden;"
                                onclick={() => {}}
                            >hidden</Button.Action>
                        {/if}
                    </Table.Head>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {#each SharedStore.failedAccounts.concat(SharedStore.accounts) as account, index}
                <Table.Row class={index < failedAccountLength ? "failed" : ""}>
                    <Table.Cell>
                        <Input.Basic
                            type="checkbox"
                            bind:group={accountSelection}
                            value={account.email_address}
                        />
                    </Table.Cell>
                    <Table.Cell>
                        {index < failedAccountLength ? "Warning" : ""}
                        {account.fullname} &lt;{account.email_address}&gt;
                    </Table.Cell>
                    <Table.Cell>
                        <Button.Basic
                            type="button"
                            class="inline"
                            style="margin-right: 5px;"
                            onclick={() => { isEditingAccount = account; }}
                        >
                            Edit
                        </Button.Basic>
                    </Table.Cell>
                    <Table.Cell>
                        <Button.Action
                            class="inline"
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

        {#if failedAccountLength === 0}
            <Button.Action
                onclick={initMailboxes}
                disabled={!SharedStore.accounts || SharedStore.accounts.length == 0}
            >
                Continue to mailbox.
            </Button.Action>
        {/if}

        <Button.Basic
            type="button"
            class="inline"
            onclick={() => { isListingAccount = false; }}
        >
            I want to add another account.
        </Button.Basic>
    {/if}
</div>
