<script lang="ts">
    import {
      isPermissionGranted,
      requestPermission,
      sendNotification,
    } from '@tauri-apps/plugin-notification';
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account, type Email, type OpenMailTaskResults } from "$lib/types";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import EditAccountForm from "$lib/ui/Layout/Landing/Register/EditAccountForm.svelte";
    import * as Button from "$lib/ui/Elements/Button";

    const mailboxController = new MailboxController();

    let editingAccount: Account | null = $state(SharedStore.failedAccounts
        ? SharedStore.failedAccounts[0]
        : null);

    async function initMailboxes(): Promise<void> {
        const response = await mailboxController.init();
        if (!response.success) {
            alert(response.message);
        } else {
            SharedStore.currentAccount = null;
            SharedStore.currentFolder = Folder.Inbox;
            await listenForNotifications();
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

<div class="register--account_list">
    {#if editingAccount}
        <h3>Edit Account</h3>
        <EditAccountForm bind:editingAccount={editingAccount}/>
    {:else}
        <h3>Add Account</h3>
        <AddAccountForm />
    {/if}

    <AccountList bind:editingAccount={editingAccount}/>

    {#if SharedStore.accounts.length > 0}
    <div>
        <Button.Action onclick={initMailboxes}>
            Continue To Inbox
        </Button.Action>
    </div>
    {/if}
</div>

<style>
    .register--account_list{
        border:1px dashed white;
        padding: 5em;
        height:100%;
    }
</style>
