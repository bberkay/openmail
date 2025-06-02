<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { getMailboxContext, type EmailSelection, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";

    const mailboxContext = getMailboxContext();

    export async function reply(
        emailSelection: EmailSelection,
        groupedUidSelection: GroupedUidSelection,
    ) {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;
        const [
            email_address,
            replyingEmailUid
        ] = groupedUidSelection[0];

        const email = SharedStore.mailboxes[
            email_address
        ].emails.current.find(
            (email) => email.uid == replyingEmailUid
        )!;

        mailboxContext.emailSelection.value = [];
        showContent(Compose, {
            originalMessageContext: {
                composeType: "reply",
                originalMessageId: email.message_id,
                originalSender: email.sender,
                originalReceiver: email.receivers,
                originalSubject: email.subject,
                originalBody: email.body,
                originalDate: email.date,
            },
        });
    };
</script>
