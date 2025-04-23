<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language, Theme } from "$lib/types";
    import Form from "$lib/ui/Components/Form";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Button from "$lib/ui/Components/Button";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { FileSystem } from "$lib/services/FileSystem";
    import { getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";

    onMount(() => {
        showAlert("info-change-alert-container", {
            content: "You can change these later.",
            type: "info",
        });
    });

    const saveInitialPreferences = async (e: Event): Promise<void> => {
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences({
            language: SharedStore.preferences.language,
            theme: SharedStore.preferences.theme,
        });
    };
</script>

<div class="alert-container" id="info-change-alert-container"></div>
<Form onsubmit={saveInitialPreferences}>
    <FormGroup>
        <Label for="language">Language</Label>
        <Select.Root
            id="language"
            placeholder="Language"
            value={getEnumKeyByValue(
                Language,
                SharedStore.preferences.language,
            )}
            onchange={(selectedOption) => {
                SharedStore.preferences.language = getEnumValueByKey(
                    Language,
                    selectedOption as keyof typeof Language,
                );
            }}
            style="width:100%"
        >
            {#each Object.entries(Language) as langEntry}
                {@const [langId, langName] = langEntry}
                <Select.Option value={langId} content={langName} />
            {/each}
        </Select.Root>
    </FormGroup>
    <FormGroup>
        <Label for="theme">Theme</Label>
        <Select.Root
            id="theme"
            placeholder="Theme"
            value={getEnumKeyByValue(Theme, SharedStore.preferences.theme)}
            onchange={(selectedOption) => {
                SharedStore.preferences.theme = getEnumValueByKey(
                    Theme,
                    selectedOption as keyof typeof Theme,
                );
            }}
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
    <div class="landing-body-footer">
        <Button.Basic type="submit" class="btn-cta">Continue</Button.Basic>
    </div>
</Form>
