<script lang="ts">
    import { Language } from "$lib/types";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { getEnumKeyByValue } from "$lib/utils";
    import { PreferenceManager, PreferenceStore } from "$lib/preferences";

    const selectLanguage = async (selectedLanguage: string) => {
        await PreferenceManager.changeLanguage(selectedLanguage as Language);
    }
</script>

<FormGroup>
    <Label for="language">Language</Label>
    <Select.Root
        id="language"
        placeholder="Language"
        value={getEnumKeyByValue(Language, PreferenceStore.language)}
        onchange={selectLanguage}
        style="width:100%"
    >
        {#each Object.entries(Language) as [langId, langName]}
            <Select.Option value={langId} content={langName} />
        {/each}
    </Select.Root>
</FormGroup>
