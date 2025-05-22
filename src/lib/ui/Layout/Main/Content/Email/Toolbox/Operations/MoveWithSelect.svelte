<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account, type Email } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { getCurrentMailbox, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { moveTo } from "./MoveTo.svelte";

    interface Props {
        account: Account;
        sourceFolder: string | Folder;
        email: Email;
        currentOffset?: number;
    }

    let {
        account,
        sourceFolder,
        email,
        currentOffset
    }: Props = $props();

    let isCurrentFolderCustom = $derived.by(() => {
        if (SharedStore.currentAccount == "home") return false;

        return SharedStore.folders[
            SharedStore.currentAccount.email_address
        ].custom.includes(sourceFolder);
    });

    const moveEmailsOnClick = async (destinationFolder: string | Folder) => {
        await moveTo(
            account,
            sourceFolder,
            destinationFolder,
            email.uid,
            currentOffset,
            email.message_id,
            false
        );
    }
</script>

<div class="tool">
    <Dropdown.Root class="dropdown-sm">
        <Dropdown.Toggle>
            {local.move_to[DEFAULT_LANGUAGE]}
        </Dropdown.Toggle>
        <Dropdown.Content>
            {#if isCurrentFolderCustom}
                <!-- Add inbox option if email is in custom folder -->
                <Dropdown.Item onclick={async () => await moveEmailsOnClick(Folder.Inbox)}>
                    {Folder.Inbox}
                </Dropdown.Item>
            {/if}
            {#each SharedStore.folders[account.email_address].custom as customFolder}
                {#if customFolder !== sourceFolder}
                    <Dropdown.Item onclick={async () => await moveEmailsOnClick(customFolder)}>
                        {customFolder}
                    </Dropdown.Item>
                {/if}
            {/each}
        </Dropdown.Content>
    </Dropdown.Root>
</div>
