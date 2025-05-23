<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Toolbox from "./Email/Toolbox.svelte";
    import Content from "./Email/Content.svelte";
    import { getCurrentMailbox } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email,
    }: Props = $props();

    let currentOffset = $state(
        getCurrentMailbox().emails.current.findIndex((em) => em.uid === email.uid) + 1
    );
</script>

<Toolbox
    {account}
    bind:email
    bind:currentOffset
/>
<Content
    {account}
    {email}
/>
