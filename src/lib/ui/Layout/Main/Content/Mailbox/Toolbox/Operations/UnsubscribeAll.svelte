<script lang="ts" module>
    import { MailboxController } from "$lib/mailbox";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { isUidInSelection, simpleDeepCopy } from "$lib/utils";

    export async function unsubscribeAll(
        groupedUidSelection: GroupedUidSelection,
    ) {
        const currentSelection = simpleDeepCopy(groupedUidSelection);
        const results = await Promise.allSettled(
            currentSelection.map(async ([email_address, uids]) => {
                const account = SharedStore.accounts.find(
                    (acc) => acc.email_address === email_address,
                )!;

                const emails = SharedStore.mailboxes[
                    email_address
                ].emails.current.filter((email) => {
                    return (
                        isUidInSelection(uids, email.uid) &&
                        email.list_unsubscribe
                    );
                });

                const unsubscribeResultOfAccount = await Promise.allSettled(
                    emails.map(async (email) => {
                        const response = await MailboxController.unsubscribe(
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
                    throw new Error(
                        "one or more unsubscribe operations have failed.",
                    );
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
    }
</script>
