<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language } from "$lib/types";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
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

<FormGroup>
    <Label for="language">Language</Label>
    <Select.Root
        id="language"
        placeholder="Language"
        value={getEnumKeyByValue(
            Language,
            SharedStore.preferences.language,
        )}
        onchange={selectLanguage}
        style="width:100%"
    >
        {#each Object.entries(Language) as [langId, langName]}
            <Select.Option value={langId} content={langName} />
        {/each}
    </Select.Root>
</FormGroup>
