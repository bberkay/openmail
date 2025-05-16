<script lang="ts" module>
    export async function forward() {
        // Check out `unsubscribe()`
        if (emailSelection.length > 1) return;

        const emailAddressOfSelection = groupedEmailSelection[0][0];
        const forwardingEmailUid = groupedEmailSelection[0][1];

        const email = SharedStore.mailboxes[
            emailAddressOfSelection
        ].emails.current.find((email) => email.uid == forwardingEmailUid)!;

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
