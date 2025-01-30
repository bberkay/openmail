<script lang="ts">
    import { MailboxController } from "$lib/controllers/MailboxController";
    import type { Account, EmailSummary } from "$lib/types";
    import Button from "$lib/ui/Elements/Button";
    import Email from "../Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    const mailboxController = new MailboxController();

    interface Props {
        account: Account;
        folder: string;
        email: EmailSummary;
    }

    let { account, folder, email }: Props = $props();

    const getEmailContent = async (): Promise<void> => {
        const response = await mailboxController.getEmailContent(account, folder, email.uid);

        if (response.success && response.data) {
            showContent(Email, {account: account, email: response.data});
        } else {
            alert(response.message);
        }
    }
</script>

<div>
    <pre>{JSON.stringify(email, null, 2)}</pre>
    <Button.Action onclick={getEmailContent} style="margin-top:10px">
        Show Content
    </Button.Action>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class="tag">{flag}</span>
        {/each}
    {/if}
</div>
<br>
