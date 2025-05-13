<script lang="ts">
    import { locale } from "@tauri-apps/plugin-os";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { convertToLanguageEnum, convertToRFC5646Format, getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";
    import { onMount } from "svelte";
    import { DEFAULT_PREFERENCES } from "$lib/constants";

    let newLanguage: Language = $state(SharedStore.preferences.language);

    onMount(() => {
        document.removeEventListener("preferencesSaved", saveLanguageChange);
        document.addEventListener("preferencesSaved", saveLanguageChange);
        document.removeEventListener("preferencesResetToDefault", resetLanguage);
        document.addEventListener("preferencesResetToDefault", resetLanguage);
    });

    function saveLanguageChange() {
        SharedStore.preferences.language = newLanguage;

        // Check out app.html
        localStorage.setItem("language", document.documentElement.getAttribute("lang")!);
    }

    function resetLanguage() {
        changeLanguage(DEFAULT_PREFERENCES.language);
        saveLanguageChange();
    }

    const changeLanguage = async (selectedLanguage: string) => {
        newLanguage = getEnumValueByKey(
            Language,
            selectedLanguage as keyof typeof Language,
        );

        let foundLocale = "";
        if (newLanguage === Language.System) {
            const preferredLocale = await locale();
            foundLocale = preferredLocale
                ? convertToLanguageEnum(preferredLocale) || Language.EN_US
                : Language.EN_US;
        } else {
            foundLocale = newLanguage;
        }

        document.documentElement.setAttribute(
            "lang",
            convertToRFC5646Format(foundLocale)
        );
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Language</span>
        <small class="muted">Change your language</small>
    </div>
    <div class="settings-section-body">
        <Select.Root
            class="select-sm"
            id="language"
            placeholder="Language"
            value={getEnumKeyByValue(
                Language,
                SharedStore.preferences.language,
            )}
            onchange={changeLanguage}
            disableClearButton={true}
        >
            {#each Object.entries(Language) as [langId, langName]}
                <Select.Option value={langId} content={langName} />
            {/each}
        </Select.Root>
    </div>
</div>
