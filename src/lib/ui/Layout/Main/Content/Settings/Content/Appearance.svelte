<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Theme } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
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

<div class="settings-content-header">
    <h1 class="settings-content-title">Appearance</h1>
    <span class="settings-content-description muted">These are general settings for your application.</span>
</div>
<div class="settings-content-body">
    <div class="settings-section">
        <div class="settings-section-title">
            <span>Theme</span>
            <small class="muted">Change your goddmandl angue</small>
        </div>
        <div class="settings-section-body">
            <Select.Root
                id="theme"
                placeholder="Theme"
                value={getEnumKeyByValue(Theme, SharedStore.preferences.theme)}
                onchange={selectTheme}
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
        </div>
    </div>
</div>
