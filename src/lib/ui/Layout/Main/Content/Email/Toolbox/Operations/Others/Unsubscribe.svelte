<script lang="ts" module>
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account, type Email } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import { getCurrentMailbox, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    export async function unsubscribe(
        account: Account,
        email: Email
    ) {
        if (!email.list_unsubscribe) return;

        const response = await MailboxController.unsubscribe(
            account,
            email.list_unsubscribe!,
            email.list_unsubscribe_post,
        );

        if (!response.success) {
            showMessage({
                title: local.error_unsubscribe_s[DEFAULT_LANGUAGE],
            });
            console.error(response.message);
            return;
        }

        showToast({ content: "Unsubscribed" });
    };
</script>

<script lang="ts">
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet,
        account: Account,
        email: Email
    }

    let {
        children,
        account,
        email
    } = $props();

    const unsubscribeOnClick = async () => {
        await unsubscribe(
            account,
            email
        );
    }
</script>

<Dropdown.Item onclick={unsubscribeOnClick}>
    {@render children()}
</Dropdown.Item>
