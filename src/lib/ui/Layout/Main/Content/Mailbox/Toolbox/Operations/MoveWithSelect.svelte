<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { getCurrentMailbox, type GroupedUidSelection } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { moveTo } from "./MoveTo.svelte";

    interface Props {
        groupedUidSelection: GroupedUidSelection;
        sourceFolder: string | Folder;
    }

    let {
        groupedUidSelection = $bindable(),
        sourceFolder,
    }: Props = $props();

    let email_address = $derived(groupedUidSelection[0][0]);
    let isCurrentFolderCustom = $derived.by(() => {
        if (SharedStore.currentAccount == "home") return false;

        return SharedStore.folders[
            SharedStore.currentAccount.email_address
        ].custom.includes(getCurrentMailbox().folder);
    });

    const moveEmailsOnClick = async (destinationFolder: string | Folder) => {
        await moveTo(
            groupedUidSelection,
            sourceFolder,
            destinationFolder,
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
            {#each SharedStore.folders[email_address].custom as customFolder}
                {#if SharedStore.currentAccount === "home" || customFolder !== getCurrentMailbox().folder}
                    <Dropdown.Item onclick={async () => await moveEmailsOnClick(customFolder)}>
                        {customFolder}
                    </Dropdown.Item>
                {/if}
            {/each}
        </Dropdown.Content>
    </Dropdown.Root>
</div>
