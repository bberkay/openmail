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

<!--
TODO: Burada patladık çünkü eski tabloya göre yaptık
halbuki yeni list.html a göre yapmak lazımdı özellikle
checkbox-cell gibi css ler falan  yok, o yüzden sen
bunu bir daha list.html a yaparak yap. Ayrıca
hem buradaki style.css .landing-container a
hem de list.html da kullanılan css de ki .landing-container
a dikkat et.

Bir de landing footer muhabbeti var o ne olacak?
-->
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
                    <Table.Head class="checkbox-cell">
                        <Input.Basic
                            type="checkbox"
                            onclick={selectAllAccounts}
                        />
                    </Table.Head>
                    <Table.Head class="body-cell">
                        Account{accountSelection.length > 0 ? ` (${accountSelection.length} selected)` : ""}
                    </Table.Head>
                    <Table.Head>
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
                            class="inline"
                            style="margin-right: 5px;"
                            onclick={() => { isEditingAccount = account; }}
                        >
                            Edit
                        </Button.Basic>
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

        <div class="landing-body-footer">
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
