<script lang="ts" module>
    export async function unsubscribeAll() {
        const currentSelection = simpleDeepCopy(groupedEmailSelection);
        const results = await Promise.allSettled(
            currentSelection.map(async (group) => {
                const emailAddress = group[0];
                const uids = group[1];

                const account = SharedStore.accounts.find(
                    (acc) => acc.email_address === emailAddress,
                )!;

                const emails = SharedStore.mailboxes[
                    emailAddress
                ].emails.current.filter((email) => {
                    return (
                        isUidInSelection(uids, email.uid) &&
                        email.list_unsubscribe
                    );
                });

                const unsubscribeResultOfAccount = await Promise.allSettled(
                    emails.map(async (email) => {
                        const response =
                            await MailboxController.unsubscribe(
                                account,
                                email.list_unsubscribe!,
                                email.list_unsubscribe_post,
                            );

                        if (!response.success) {
                            throw new Error(response.message);
                        }
                    }),
                );

                const failed = unsubscribeResultOfAccount.filter(
                    (r) => r.status === "rejected",
                );
                if (failed.length > 0) {
                    failed.forEach((f) => console.error(f.reason));
                    throw new Error("one or more unsubscribe operations have failed.");
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");
        if (failed.length > 0) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
            if (failed.length === results.length) return;
        }

        showToast({ content: "success unsubscribe" });
    };
</script>
