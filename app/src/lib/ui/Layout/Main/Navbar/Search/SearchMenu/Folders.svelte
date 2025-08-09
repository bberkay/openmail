<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { Folder, type Account } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import * as Select from "$lib/ui/Components/Select";

    interface Props {
        searchingAccounts: "home" | Account[];
        searchingFolder: string | Folder
    }

    let {
        searchingAccounts = $bindable(),
        searchingFolder = $bindable()
    }: Props = $props();

    let standardFolders: string[] = $derived(
        searchingAccounts !== "home" && searchingAccounts.length === 1
            ? SharedStore.folders[
                searchingAccounts[0].email_address
            ].standard
            : [],
    );

    let customFolders: string[] = $derived(
        searchingAccounts !== "home" && searchingAccounts.length === 1
            ? SharedStore.folders[
                searchingAccounts[0].email_address
            ].custom
            : [],
    );

    const selectFolder = (selectedFolder: string | Folder) => {
        searchingFolder = selectedFolder;
    };
</script>

<FormGroup>
    <Label for="searching-folder">{local.folder[DEFAULT_LANGUAGE]}</Label>
    {#if searchingAccounts.length > 1}
        <Select.Root
            id="searching-folder"
            value={Folder.All}
            style="width:100%;"
            onchange={() => {}}
            disabled={true}
        >
            <Select.Option value={Folder.All} content={Folder.All} />
        </Select.Root>
    {:else}
        <Select.Root
            id="searching-folder"
            value={Folder.All}
            style="width:100%;"
            onchange={selectFolder}
        >
            {#each standardFolders as standardFolder}
                {@const [folderTag, ] =
                    standardFolder.split(":")}
                <Select.Option
                    value={folderTag}
                    content={folderTag}
                />
            {/each}
            <Select.Separator />
            {#each customFolders as customFolder}
                <Select.Option
                    value={customFolder}
                    content={customFolder}
                />
            {/each}
        </Select.Root>
    {/if}
</FormGroup>
