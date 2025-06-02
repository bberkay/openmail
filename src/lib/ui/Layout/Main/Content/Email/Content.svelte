<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Body from "./Content/Body.svelte";
    import Attachments from "./Content/Attachments.svelte";
    import Subject from "./Content/Subject.svelte";
    import Flags from "./Content/Flags.svelte";
    import Sender from "./Content/Sender.svelte";
    import { getMailboxContext } from "../Mailbox";

    interface Props {
        account: Account;
        email: Email;
    }

    let { account, email }: Props = $props();

    const mailboxContext = getMailboxContext();
</script>

<div class="email-content">
    <Flags {email} />
    <Subject {email} />
    <Sender {account} {email} />
    <div class="separator" style="margin: var(--spacing-md) 0"></div>
    <Body {email} />
    {#if email.attachments}
        <div class="separator"></div>
        <Attachments
            {account}
            {email}
            folder={mailboxContext.getCurrentMailbox().folder}
        />
    {/if}
</div>

<style>
    :global {
        .email-content {
            width: 80%;
            padding: var(--spacing-lg);
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-sm);
            overflow-x: hidden;
            overflow-y: scroll;
        }
    }
</style>
