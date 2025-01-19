<script lang="ts">
    import type { EmailSummary, EmailWithContent } from "$lib/types";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";

    interface Props {
        owner: string;
        email: EmailSummary;
        showContent: (email: EmailWithContent) => void;
    }

    let { owner, email, showContent }: Props = $props();

    const mailboxController = new MailboxController();

    async function getEmailContent(){
        const response = await mailboxController.getEmailContent(owner, email.uid);

        if (response.success && response.data) {
            showContent(response.data);
        } else {
            alert(response.message);
        }
    }
</script>

<div>
    <pre>{JSON.stringify(email, null, 2)}</pre>

    <ActionButton id="get-email-content" operation={getEmailContent} style="margin-top:10px">
        Show Content
    </ActionButton>
    {#if Object.hasOwn(email, "flags") && email.flags}
        {#each email.flags as flag}
            <span class="tag">{flag}</span>
        {/each}
    {/if}
</div>
<br>
