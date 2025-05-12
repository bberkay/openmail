<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Theme } from "$lib/types";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { convertToThemeEnum, getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";
    import { getCurrentWindow } from "@tauri-apps/api/window";

    const selectTheme = async (selectedTheme: string) => {
        SharedStore.preferences.theme = getEnumValueByKey(
            Theme,
            selectedTheme as keyof typeof Theme,
        );

        let foundTheme = "";
        if(SharedStore.preferences.theme === Theme.System) {
            const preferredTheme = await getCurrentWindow().theme();
            foundTheme = (preferredTheme
                ? convertToThemeEnum(preferredTheme) || Theme.Dark
                : Theme.Dark).toLowerCase();
        } else {
            foundTheme = SharedStore.preferences.theme.toLowerCase();
        }

        document.documentElement.setAttribute("data-color-scheme", foundTheme);
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
        {#each Object.entries(Theme) as themeEntry}
            {@const [themeId, themeName] = themeEntry}
            <Select.Option
                value={themeId}
                content={themeName}
                icon={themeId.toLowerCase()}
            />
        {/each}
    </Select.Root>
</FormGroup>
