<script lang="ts">
    import {
      isPermissionGranted,
      requestPermission,
      sendNotification,
    } from '@tauri-apps/plugin-notification';
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import type { Account, Email as EmailAsType } from "$lib/types";
    import { onMount } from 'svelte';
    import * as Button from "$lib/ui/Elements/Button";
    import Email from "../Email.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";

    const mailboxController = new MailboxController();

    interface Props {
        account: Account;
        folder: string;
        email: EmailAsType;
    }

    let { account, folder, email }: Props = $props();
    let isThisNew: boolean = $state(false);

    const getEmailContent = async (): Promise<void> => {
        const response = await mailboxController.getEmailContent(account, folder, email.uid);

        if (response.success && response.data) {
            showContent(Email, {account: account, email: response.data});
        } else {
            alert(response.message);
        }
    }

    $effect(() => {
        if (SharedStore.recentEmails.length > 0) {
            const recentEmails = SharedStore.recentEmails.find(
                a => a.email_address === account.email_address
            );
            isThisNew = recentEmails !== undefined
                && recentEmails.email_address == account.email_address
                && recentEmails.result.includes(email.uid);
        }
    });
</script>

<div>
    {#if isThisNew}
        <div style="background-color:dodgerblue;color:white;border-radius: 15px;padding:2px;">
            New
        </div>
    {/if}
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
