<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import Icon from "$lib/ui/Components/Icon";

    const refresh = async (): Promise<void> => {
        const accounts =
            SharedStore.currentAccount !== "home"
                ? [SharedStore.currentAccount]
                : SharedStore.accounts;

        const results = await Promise.allSettled(
            accounts.map(async (account) => {
                const response = await MailboxController.getMailbox(account);
                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({
                title: local.error_refresh_mailbox_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        showToast({ content: "mailbox is refreshred" });
    };
</script>

<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet
    }

    let { children } = $props();

    const refreshOnClick = async () => {
        await refresh();
    }
</script>

<div class="tool">
    <Button.Action
        type="button"
        class="btn-inline"
        onclick={refreshOnClick}
    >
        {@render children()}
    </Button.Action>
</div>
