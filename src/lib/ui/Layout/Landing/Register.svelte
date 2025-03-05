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

    let isEditingAccount: Account | null = $state(null);
    let isListingAccount: boolean = $state(SharedStore.failedAccounts.length > 0);
</script>

<div class="register--account_list">
    <div class="header">
        <h1>{
            isEditingAccount
                ? "Edit account."
                : isListingAccount
                    ? "Added accounts."
                    : "Add a new account."
            }
        </h1>
    </div>
    <div class="body">
        {#if isEditingAccount}
            <EditAccountForm bind:isEditingAccount={isEditingAccount}/>
        {:else if isListingAccount}
            <AccountList bind:isEditingAccount={isEditingAccount}/>
        {:else}
            <AddAccountForm />
        {/if}

        {#if !isEditingAccount}
            <div class="buttons">
                <Button.Action onclick={initMailboxes} disabled={SharedStore.accounts.length == 0}>
                    Continue to mailbox.
                </Button.Action>
                {#if isListingAccount}
                    <button onclick={() => { isListingAccount = false; }}>Add a new account.</button>
                {:else}
                    <button onclick={() => { isListingAccount = true; }}>Show added accounts.</button>
                {/if}
            </div>
        {/if}
    </div>
</div>

<style>
    .register--account_list{
        display: flex;
        flex-direction: column;
        background-color: #111;
        border: 1px dashed #333;
        border-top: none;
        border-bottom: none;
        height: 100%;
        width: 700px;

        & .header{
            padding: 2em 1.5em 1em 1.5em;
            border-bottom: 1px dashed #333;
        }

        & .body {
            padding: 1.5em;
            display:flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;

            :global(& form input) {
                width: 100%;
                border:1px solid #444;
                background-color: #333;
                border-radius: 0;
            }

            & .buttons {
                display: flex;
                gap: 7px;
                margin-top: 1em;

                :global(& button) {
                    flex:1;
                    padding: 5px;
                    border:1px solid #444;
                    background-color:#222;
                    border-radius:0;
                }
            }
        }
    }
</style>
