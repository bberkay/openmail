<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Language, Theme } from "$lib/types";
    import { ApiService, PostRoutes } from "$lib/services/ApiService";
    import Form from "$lib/ui/Components/Form";
    import { FormGroup } from "$lib/ui/Components/Form";
    import * as Button from "$lib/ui/Components/Button";
    import * as Select from "$lib/ui/Components/Select";
    import Icon from "$lib/ui/Components/Icon/Icon.svelte";
    import Label from "$lib/ui/Components/Label";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { fileSystem } from "$lib/services/FileSystem";

    let selectedLanguage: Language = $state(SharedStore.preferences.language);
    let selectedTheme: Theme = $state(SharedStore.preferences.theme);

    onMount(() => {
        showAlert("info-change-alert-container", {
            content: "You can change these later.",
            type: "info"
        });
    })

    const saveInitialPreferences = async (e: Event): Promise<void> => {
        await fileSystem.savePreferences({
            language: selectedLanguage,
            theme: selectedTheme,
        });
    };
</script>

<div class="alert-container" id="info-change-alert-container"></div>
<Form onsubmit={saveInitialPreferences}>
    <div>
        <FormGroup>
            <Label for="language">Language</Label>
            <Select.Root
                id="language"
                placeholder="Language"
                value={SharedStore.preferences.language}
                onchange={(selectedOption) => {
                    selectedLanguage = selectedOption as Language;
                }}
            >
                {#each Object.entries(Language) as langEntry}
                    {@const [langId, langName] = langEntry}
                    <Select.Option value={langId}>{langName}</Select.Option>
                {/each}
            </Select.Root>
        </FormGroup>
        <FormGroup direction="horizontal">
            {#each Object.entries(Theme) as themeEntry}
                {@const [themeId, themeName] = themeEntry}

                <Button.Basic
                    class="btn-inline theme"
                    onclick={() => {
                        selectedTheme = themeId as Theme;
                    }}
                >
                    <Icon name={themeId.toLowerCase()} />
                    <span>{themeName}</span>
                </Button.Basic>
            {/each}
        </FormGroup>
        <div class="landing-body-footer">
            <Button.Basic type="submit">Continue</Button.Basic>
        </div>
    </div>
</Form>

<style>
    :global {
        .theme {
            display: "flex";
            flex-direction: column;
            justify-content: center;
            gap: var(--spacing-sm);
        }
    }
</style>
