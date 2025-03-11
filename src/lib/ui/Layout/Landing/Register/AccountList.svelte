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
</script>

<div>
    {#if SharedStore.failedAccounts.length > 0}
        <div class="alert error" style="margin-bottom:15px;">
            <span>
                ⚠ There were {SharedStore.failedAccounts.length} accounts that failed to
                connect.
            </span>
        </div>
    {/if}

    {#if
        (SharedStore.accounts && SharedStore.accounts.length > 0)
        || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)
    }
        {@const failedAccountLength = (SharedStore.failedAccounts || []).length}
        <table>
            <thead>
                <tr>
                    <th><input type="checkbox" onclick={selectAllAccounts}></th>
                    <th>Account{accountSelection.length > 0 ? ` (${accountSelection.length} selected)` : ""}</th>
                    <th colspan="2">
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
                            >
                                invisible
                            </Button.Action>
                        {/if}
                    </th>
                </tr>
            </thead>
            <tbody>
                {#each SharedStore.failedAccounts.concat(SharedStore.accounts) as account, index}
                <tr class={index < failedAccountLength ? "failed" : ""}>
                    <td><input type="checkbox" bind:group={accountSelection} value={account.email_address}></td>
                    <td>
                        {index < failedAccountLength ? "Warning" : ""}
                        {account.fullname} &lt;{account.email_address}&gt;
                    </td>
                    <td>
                        <button
                            class="inline"
                            style="margin-right: 5px;"
                            onclick={() => {
                                isEditingAccount = account;
                            }}
                        >
                            Edit
                        </button>
                    </td>
                    <td>
                        <Button.Action
                            class="inline"
                            onclick={removeAccount}
                            data-email-address={account.email_address}
                        >
                            Remove
                        </Button.Action>
                    </td>
                </tr>
                {/each}
            </tbody>
        </table>

        {#if failedAccountLength === 0}
            <Button.Action onclick={initMailboxes} disabled={!SharedStore.accounts || SharedStore.accounts.length == 0}>
                Continue to mailbox.
            </Button.Action>
        {/if}

        <div class="add-account-navigation">
            <button onclick={() => { isListingAccount = false; }}>I want to add another account.</button>
        </div>
    {/if}
</div>

<style>
    .add-account-navigation {
        text-align: center;
        margin-top: 20px;
    }
</style>
