<script lang="ts" module>
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import {
        type EmailSelection,
        type GroupedUidSelection,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    export async function unsubscribe(
        emailSelection: EmailSelection,
        groupedUidSelection: GroupedUidSelection,
    ) {
        // Since "unsubscribe/reply/forward" options are disabled when there is
        // more than one current account("home"), groupedEmailSelection's length
        // isn't going to be more than 1, so first index is enough to cover
        // selection.
        if (emailSelection.length > 1) return;

        const [email_address, uid] = groupedUidSelection[0];
        const email = SharedStore.mailboxes[email_address].emails.current.find(
            (em) => em.uid == uid,
        )!;

        if (!email.list_unsubscribe) return;

        const response = await MailboxController.unsubscribe(
            SharedStore.accounts.find(
                (account) => account.email_address === email_address,
            )!,
            email.list_unsubscribe,
            email.list_unsubscribe_post,
        );

        if (!response.success) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        showToast({ content: "Unsubscribe success" });
    }
</script>
