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
    import { convertToLanguageEnum, convertToRFC5646Format, convertToThemeEnum, getEnumKeyByValue, getEnumValueByKey } from "$lib/utils";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import AccountList from "$lib/ui/Layout/Landing/Register/AccountList.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Landing/Register.svelte";
    import { getCurrentWindow } from "@tauri-apps/api/window";
    import { locale } from "@tauri-apps/plugin-os";

    onMount(() => {
        showAlert("info-change-alert-container", {
            content: "You can change these later.",
            type: "info",
        });
    });

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

    const saveInitialPreferences = async (e: Event): Promise<void> => {
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences({
            language: SharedStore.preferences.language,
            theme: SharedStore.preferences.theme,
        });

        localStorage.setItem("theme", SharedStore.preferences.theme.toLowerCase());
        localStorage.setItem(
            "language",
            convertToRFC5646Format(
                getEnumKeyByValue(Language, SharedStore.preferences.language)!,
            )
        );

        showContent(
            SharedStore.accounts.length > 0 ||
                SharedStore.failedAccounts.length > 0
                ? AccountList
                : AddAccountForm,
        );
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
            onchange={selectLanguage}
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
            onchange={selectTheme}
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
