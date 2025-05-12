<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        getFailedAccountsTemplate,
        getFailedItemTemplate,
    } from "$lib/templates";
    import { type Account } from "$lib/types";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { createSenderAddress, isStandardFolder } from "$lib/utils";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import EditAccountForm from "./EditAccountForm.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Landing/Register.svelte";
    import AddAccountForm from "./AddAccountForm.svelte";
    import AccountTable from "./AccountList/AccountTable.svelte";
    import { NotificationHandler } from "$lib/services/NotificationHandler";

    const ACCOUNT_COUNT_PER_PAGE = 5;

    /**
     * Create WebSocket connections
     * for every account to receive
     * new email notifications.
     */
    async function listenForNotifications() {
        SharedStore.accounts.forEach((account) => new NotificationHandler(account));
    }

    function printFailedAccounts() {
        return getFailedAccountsTemplate(
            SharedStore.failedAccounts
                .map((account) => {
                    return getFailedItemTemplate(
                        createSenderAddress(
                            account.email_address,
                            account.fullname,
                        ),
                    );
                })
                .join(""),
        );
    }

    function manageFailedAccounts() {
        showEditAccount(SharedStore.failedAccounts[0]);
    }

    const initMailboxes = async () => {
        const response = await MailboxController.init();
        if (!response.success) {
            console.error(response.message);
            showMessage({
                title: local.error_initialize_mailboxes[DEFAULT_LANGUAGE],
            });
        }
        // TODO: Open this later.
        //await listenForNotifications();
    }

    const showEditAccount = (account: Account) => {
        showContent(EditAccountForm, {
            account,
        });
    };

    const showAddAccount = () => {
        showContent(AddAccountForm);
    };

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("accounts-alert-container", {
                content: local.accounts_failed_to_connect[DEFAULT_LANGUAGE],
                type: "error",
                details: printFailedAccounts(),
                onManageText: local.manage_accounts[DEFAULT_LANGUAGE],
                onManage: manageFailedAccounts,
                closeable: false,
            });
        } else if (SharedStore.accounts.length === 0) {
            showAlert("accounts-alert-container", {
                content: "You havent add any account.",
                type: "warning",
            });
        }
    });
</script>

<div>
    <div class="alert-container" id="accounts-alert-container"></div>
    {#if SharedStore.accounts.length === 0 && SharedStore.failedAccounts.length === 0}
        <Button.Basic type="button" class="btn-cta" onclick={showAddAccount}>
            Add an account
        </Button.Basic>
    {:else}
        <AccountTable
            accountsPerPage={ACCOUNT_COUNT_PER_PAGE}
            {showEditAccount}
        />

        <div class="landing-body-footer">
            <Button.Action
                class="btn-cta"
                onclick={initMailboxes}
                disabled={!SharedStore.accounts ||
                    SharedStore.accounts.length == 0}
            >
                {local.continue_to_mailbox[DEFAULT_LANGUAGE]}
            </Button.Action>
            <Button.Basic
                type="button"
                class="btn-inline"
                onclick={showAddAccount}
            >
                {local.add_another_account[DEFAULT_LANGUAGE]}
            </Button.Basic>
        </div>
    {/if}
</div>
