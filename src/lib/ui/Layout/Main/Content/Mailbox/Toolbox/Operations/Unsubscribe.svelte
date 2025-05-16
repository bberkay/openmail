<script lang="ts" module>
    export async function unsubscribe() {
        // Since "unsubscribe/reply/forward" options are disabled when there is
        // more than one current account("home"), groupedEmailSelection's length
        // isn't going to be more than 1, so first index is enough to cover
        // selection.
        if (emailSelection.length > 1) return;

        const emailAddress = groupedEmailSelection[0][0];
        const uid = groupedEmailSelection[0][1];
        const email = SharedStore.mailboxes[emailAddress].emails.current.find(
            (em) => em.uid == uid,
        )!;

        if (!email.list_unsubscribe) return;

        const response = await MailboxController.unsubscribe(
            SharedStore.accounts.find(
                (account) => account.email_address === emailAddress,
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
    };
</script>
