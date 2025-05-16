<script lang="ts" module>
    export async function reply() {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;

        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const replyingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((email) => email.uid == replyingEmailUid)!;

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
