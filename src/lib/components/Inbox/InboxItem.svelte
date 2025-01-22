<script lang="ts">
    import type { EmailSummary, EmailWithContent } from "$lib/types";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { show as showContent } from "$lib/components/Content.svelte";
    import Email from "../Email/Email.svelte";

    interface Props {
        owner: string;
        folder: string;
        email: EmailSummary;
    }

    let { owner, folder, email }: Props = $props();

    const mailboxController = new MailboxController();

    const getEmailContent = async (): Promise<void> => {
        const response = await mailboxController.getEmailContent(owner, folder, email.uid);

        if (response.success && response.data) {
            showContent(Email, response.data);
        } else {
            alert(response.message);
        }
    }
</script>

<div>
    <pre>{JSON.stringify(email, null, 2)}</pre>

    <ActionButton onclick={getEmailContent} style="margin-top:10px">
        Show Content
    </ActionButton>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class="tag">{flag}</span>
        {/each}
    {/if}
</div>
<br>
