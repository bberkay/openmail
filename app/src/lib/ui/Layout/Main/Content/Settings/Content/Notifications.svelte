<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import AccountTable from "./Notifications/AccountTable.svelte";
    import Accounts from "./Accounts.svelte";
    import { showThis as showContent } from "../Content.svelte";

    const ACCOUNTS_PER_PAGE = 5;

    function manageFailedAccounts() {
        showContent(Accounts);
    }

    $effect(() => {
        if (SharedStore.failedAccounts.length > 0) {
            showAlert("check-out-settings-accounts-alert-container", {
                content: local.accounts_failed_to_connect[DEFAULT_LANGUAGE],
                type: "error",
                details: `There are some failed account/mailbox connections you should manage.
                Failed accounts will not be shown in notification settings!`,
                onManage: manageFailedAccounts,
                onManageText: local.manage_accounts[DEFAULT_LANGUAGE],
                closeable: true,
            });
        }
    });
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">Notifications</h1>
    <span class="settings-content-description muted">
        These are accounts settings.
    </span>
</div>
<div class="settings-content-body">
    <div
        class="alert-container"
        id="check-out-settings-accounts-alert-container"
    ></div>
    <AccountTable accountsPerPage={ACCOUNTS_PER_PAGE} />
</div>
