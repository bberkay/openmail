<script lang="ts" module>
    import { type Email } from "$lib/types";
    import Compose from "$lib/ui/Layout/Main/Content/Compose.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    export function reply(email: Email) {
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
    }
</script>

<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";

    interface Props {
        children: Snippet,
        email: Email
    }

    let {
        children,
        email
    }: Props = $props();

    const mailboxContext = getMailboxContext();

    const replyOnClick = () => {
        reply(email);
        mailboxContext.emailSelection.value = [];
    }
</script>

<div class="tool">
    <Button.Basic
        type="button"
        class="btn-inline"
        onclick={replyOnClick}
    >
        {@render children()}
    </Button.Basic>
</div>
