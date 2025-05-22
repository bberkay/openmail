<script lang="ts">
    import { markEmails, unmarkEmails } from "../Toolbox/Operations/MarkAs.svelte";
    import * as Context from "$lib/ui/Components/Context";
    import { type Mark, Folder } from "$lib/types";
    import type { Snippet } from "svelte";
    import type { GroupedUidSelection } from "../../Mailbox.svelte";

    interface Props {
        children: Snippet,
        groupedUidSelection: GroupedUidSelection;
        markType: Mark;
        folder: string | Folder;
        isUnmark?: boolean;
    }

    let {
        children,
        groupedUidSelection = $bindable(),
        markType,
        folder,
        isUnmark = false
    }: Props = $props();

    const markEmailsOnClick = async () => {
        await markEmails(groupedUidSelection, markType, folder);
    };

    const unmarkEmailsOnClick = async () => {
        await unmarkEmails(groupedUidSelection, markType, folder);
    };
</script>

{#if isUnmark}
    <Context.Item onclick={markEmailsOnClick}>
        {@render children()}
    </Context.Item>
{:else}
    <Context.Item onclick={unmarkEmailsOnClick}>
        {@render children()}
    </Context.Item>
{/if}
