<script lang="ts">
    import { PreferenceManager } from "$lib/managers/PreferenceManager";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";
    import { Theme } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import {
        getEnumKeyByValue,
    } from "$lib/utils";

    const changeTheme = async (selectedTheme: string) => {
        await PreferenceManager.changeTheme(selectedTheme as Theme);
    };
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Theme</span>
        <small class="muted">Change your theme</small>
    </div>
    <div class="settings-section-body">
        <Select.Root
            id="theme"
            class="select-sm"
            placeholder="Theme"
            value={getEnumKeyByValue(Theme, PreferencesStore.theme)}
            onchange={changeTheme}
            disableClearButton={true}
        >
            {#each Object.entries(Theme) as [themeId, themeName]}
                <Select.Option
                    value={themeId}
                    content={themeName}
                    icon={themeId.toLowerCase()}
                />
            {/each}
        </Select.Root>
    </div>
</div>
