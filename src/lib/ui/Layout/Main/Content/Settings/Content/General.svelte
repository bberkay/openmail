<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { convertToLanguageEnum, convertToRFC5646Format, getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";
    import { locale } from "@tauri-apps/plugin-os";

    const selectLanguage = async (selectedLanguage: string) => {
        SharedStore.preferences.language = getEnumValueByKey(
            Language,
            selectedLanguage as keyof typeof Language,
        );

        let foundLocale = "";
        if (SharedStore.preferences.language === Language.System) {
            const preferredLocale = await locale();
            foundLocale = preferredLocale
                ? convertToLanguageEnum(preferredLocale) || Language.EN_US
                : Language.EN_US;
        } else {
            foundLocale = SharedStore.preferences.language;
        }

        document.documentElement.setAttribute(
            "lang",
            convertToRFC5646Format(foundLocale)
        );
    }
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">General</h1>
    <span class="settings-content-description muted">These are general settings for your application.</span>
</div>
<div class="settings-content-body">
    <div class="settings-section">
        <div class="settings-section-title">
            <span>Language</span>
            <small class="muted">Change your goddmandl angue</small>
        </div>
        <div class="settings-section-body">
            <Select.Root
                id="language"
                placeholder="Language"
                value={getEnumKeyByValue(
                    Language,
                    SharedStore.preferences.language,
                )}
                onchange={selectLanguage}
            >
                {#each Object.entries(Language) as langEntry}
                    {@const [langId, langName] = langEntry}
                    <Select.Option value={langId} content={langName} />
                {/each}
            </Select.Root>
        </div>
    </div>
    <div class="settings-section">
        <div class="settings-section-title">
            <span>Language</span>
            <small class="muted">Change your goddmandl angue</small>
        </div>
        <div class="settings-section-body">
            <Select.Root
                id="language"
                placeholder="Language"
                value={getEnumKeyByValue(
                    Language,
                    SharedStore.preferences.language,
                )}
                onchange={selectLanguage}
            >
                {#each Object.entries(Language) as langEntry}
                    {@const [langId, langName] = langEntry}
                    <Select.Option value={langId} content={langName} />
                {/each}
            </Select.Root>
        </div>
    </div>
</div>
