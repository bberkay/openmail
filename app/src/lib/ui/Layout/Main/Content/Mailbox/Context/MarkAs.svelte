<script lang="ts">
    import {
        markEmails,
        unmarkEmails,
    } from "../Toolbox/Operations/MarkAs.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { type Mark, Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import { getMailboxContext } from "../../Mailbox";

    interface Props {
        children: Snippet;
        markType: Mark;
        folder: string | Folder;
        isUnmark?: boolean;
    }

    let { children, markType, folder, isUnmark = false }: Props = $props();

    const mailboxContext = getMailboxContext();

    const markEmailsOnClick = async () => {
        await markEmails(
            mailboxContext.getGroupedUidSelection(),
            markType,
            folder,
        );
        mailboxContext.emailSelection.value = [];
    };

    const unmarkEmailsOnClick = async () => {
        await unmarkEmails(
            mailboxContext.getGroupedUidSelection(),
            markType,
            folder,
        );
        mailboxContext.emailSelection.value = [];
    };
</script>

{#if isUnmark}
    <Context.Item onclick={unmarkEmailsOnClick}>
        {@render children()}
    </Context.Item>
{:else}
    <Context.Item onclick={markEmailsOnClick}>
        {@render children()}
    </Context.Item>
{/if}
