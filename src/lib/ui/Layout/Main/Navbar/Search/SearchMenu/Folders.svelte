<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { Folder, type Account } from "$lib/types";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import * as Select from "$lib/ui/Components/Select";

    interface Props {
        searchingFolder: string | Folder
    }

    let {
        searchingFolder = $bindable()
    }: Props = $props();

    let standardFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].standard
            : [],
    );

    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].custom
            : [],
    );

    const selectFolder = (selectedFolder: string | Folder) => {
        searchingFolder = selectedFolder;
    };
</script>

<FormGroup>
    <Label for="searching-folder">{local.folder[DEFAULT_LANGUAGE]}</Label>
    <Select.Root
        id="searching-folder"
        value={Folder.All}
        onchange={selectFolder}
    >
        {#each standardFolders as standardFolder}
            {@const [folderTag, folderName] =
                standardFolder.split(":")}
            <Select.Option
                value={folderTag}
                content={folderName}
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
</FormGroup>
