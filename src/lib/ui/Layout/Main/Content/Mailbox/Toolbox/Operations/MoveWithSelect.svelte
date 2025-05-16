<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
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

    const moveEmailsOnChange = async (destinationFolder: string | Folder) => {
        await moveTo(
            groupedUidSelection,
            sourceFolder,
            destinationFolder,
            false
        );
    }
</script>

<div class="tool">
    <Select.Root
        onchange={moveEmailsOnChange}
        placeholder={local.move_to[DEFAULT_LANGUAGE]}
    >
        {#if isCurrentFolderCustom}
            <!-- Add inbox option if email is in custom folder -->
            <Select.Option value={Folder.Inbox} content={Folder.Inbox} />
        {/if}
        {#each SharedStore.folders[email_address].custom as customFolder}
            {#if SharedStore.currentAccount === "home" || customFolder !== getCurrentMailbox().folder}
                <Select.Option value={customFolder} content={customFolder} />
            {/if}
        {/each}
    </Select.Root>
</div>
