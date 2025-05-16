<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { EmailSelection, GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";

    export async function forward(
        emailSelection: EmailSelection,
        groupedUidSelection: GroupedUidSelection,
    ) {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;
        const [
            email_address,
            forwardingEmailUid
        ] = groupedUidSelection[0];

        const email = SharedStore.mailboxes[
            email_address
        ].emails.current.find(
            (email) => email.uid == forwardingEmailUid
        )!;

        showContent(Compose, {
            originalMessageContext: {
                composeType: "forward",
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
