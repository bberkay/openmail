<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Toolbox from "./Email/Toolbox.svelte";
    import Content from "./Email/Content.svelte";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox";

    interface Props {
        account: Account;
        email: Email;
    }

    let { account, email }: Props = $props();

    const mailboxContext = getMailboxContext();

    let currentOffset = $state(
        mailboxContext
            .getCurrentMailbox()
            .emails.current.findIndex((em) => em.uid === email.uid) + 1,
    );
</script>

<Toolbox {account} bind:email bind:currentOffset />
<Content {account} {email} />
