<script lang="ts">
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Theme } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { convertToThemeEnum, getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";
    import { getCurrentWindow } from "@tauri-apps/api/window";
    import { onMount } from "svelte";

    let newTheme: Theme = $state(SharedStore.preferences.theme);

    onMount(() => {
        document.removeEventListener("preferencesSaved", saveThemeChange);
        document.addEventListener("preferencesSaved", saveThemeChange);
        document.removeEventListener("preferencesResetToDefault", resetTheme);
        document.addEventListener("preferencesResetToDefault", resetTheme);
    });

    function saveThemeChange() {
        SharedStore.preferences.theme = newTheme;

        // Check out app.html
        localStorage.setItem("theme", document.documentElement.getAttribute("data-color-scheme")!);
    }

    function resetTheme() {
        changeTheme(DEFAULT_PREFERENCES.theme);
        saveThemeChange();
    }

    const changeTheme = async (selectedTheme: string) => {
        newTheme = getEnumValueByKey(
            Theme,
            selectedTheme as keyof typeof Theme,
        );

        let foundTheme = "";
        if(newTheme === Theme.System) {
            const preferredTheme = await getCurrentWindow().theme();
            foundTheme = (preferredTheme
                ? convertToThemeEnum(preferredTheme) || Theme.Dark
                : Theme.Dark).toLowerCase();
        } else {
            foundTheme = newTheme.toLowerCase();
        }

        document.documentElement.setAttribute("data-color-scheme", foundTheme);
    }
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
             value={getEnumKeyByValue(Theme, newTheme)}
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
