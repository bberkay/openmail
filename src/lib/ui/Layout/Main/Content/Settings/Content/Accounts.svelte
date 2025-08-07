<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { getFailedAccountsTemplate, getFailedItemTemplate, getFailedMailboxOrFoldersTemplate } from "$lib/templates";
    import { createSenderAddress } from "$lib/utils";
    import { MailboxController } from "$lib/mailbox";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import AccountTable from "./Accounts/AccountTable.svelte";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import EditAccountForm from "./Accounts/EditAccountForm.svelte";

    const ACCOUNTS_PER_PAGE = 5;

    function printFailedAccounts(): string {
        return getFailedAccountsTemplate(
            SharedStore.failedAccounts
                .map((account) => {
                    return getFailedItemTemplate(
                        createSenderAddress(account.email_address, account.fullname)
                    )
                })
                .join(""),
        );
    }

    function manageFailedAccounts() {
        showModal(EditAccountForm, { account: SharedStore.failedAccounts[0] });
    }

    function printFailedMailboxesOrFolders(): string {
        return getFailedMailboxOrFoldersTemplate(
            SharedStore.accountsWithFailedMailboxes
                .map((account) => {
                    return getFailedItemTemplate(
                        createSenderAddress(account.email_address, account.fullname)
                    )
                })
                .join(""),
            SharedStore.accountsWithFailedFolders
                .map((account) => {
                    return getFailedItemTemplate(
                        createSenderAddress(account.email_address, account.fullname)
                    )
                })
                .join(""),
        );
    }

    async function manageFailedMailboxesOrFolders() {
        await MailboxController.init(true);
    }

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("failed-accounts-alert-container", {
                content: local.accounts_failed_to_connect[DEFAULT_LANGUAGE],
                type: "error",
                details: printFailedAccounts(),
                onManage: manageFailedAccounts,
                onManageText: local.manage_accounts[DEFAULT_LANGUAGE],
                closeable: false
            });
        }

        if (
            SharedStore.accountsWithFailedMailboxes.length > 0 ||
            SharedStore.accountsWithFailedFolders.length > 0
        ) {
            showAlert("failed-mailboxes-or-folders-alert-container", {
                content: local.error_failed_mailboxes_or_folders[DEFAULT_LANGUAGE],
                type: "error",
                details: printFailedMailboxesOrFolders(),
                onManage: manageFailedMailboxesOrFolders,
                onManageText: local.retry[DEFAULT_LANGUAGE],
                closeable: false
            });
        }
    });
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">Accounts</h1>
    <span class="settings-content-description muted">These are accounts settings.</span>
</div>
<div class="settings-content-body">
    <div class="alert-container" id="failed-accounts-alert-container"></div>
    <div class="alert-container" id="failed-mailboxes-or-folders-alert-container"></div>
    <AccountTable accountsPerPage={ACCOUNTS_PER_PAGE} />
</div>
