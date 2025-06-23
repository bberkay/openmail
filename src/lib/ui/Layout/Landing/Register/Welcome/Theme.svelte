<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Theme } from "$lib/types";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { getEnumKeyByValue } from "$lib/utils";
    import { AppController } from "$lib/controllers/AppController";

    const selectTheme = async (selectedTheme: string) => {
        await AppController.changeTheme(selectedTheme as Theme);
    }
</script>

<FormGroup>
    <Label for="theme">Theme</Label>
    <Select.Root
        id="theme"
        placeholder="Theme"
        value={getEnumKeyByValue(Theme, SharedStore.preferences.theme)}
        onchange={selectTheme}
        style="width:100%"
    >
        {#each Object.entries(Theme) as [themeId, themeName]}
            <Select.Option
                value={themeId}
                content={themeName}
                icon={themeId.toLowerCase()}
            />
        {/each}
    </Select.Root>
</FormGroup>
