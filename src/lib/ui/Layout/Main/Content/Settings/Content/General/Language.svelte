<script lang="ts">
    import { Language } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import {
        getEnumKeyByValue,
    } from "$lib/utils";
    import { PreferenceManager } from "$lib/managers/PreferenceManager";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";

    const changeLanguage = async (selectedLanguage: string) => {
        await PreferenceManager.changeLanguage(selectedLanguage as Language);
    };
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
                PreferencesStore.language,
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
