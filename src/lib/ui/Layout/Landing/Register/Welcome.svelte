<script lang="ts">
    import { onMount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Form from "$lib/ui/Components/Form";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { FileSystem } from "$lib/services/FileSystem";
    import { convertToRFC5646Format, getEnumKeyByValue } from "$lib/utils";
    import AddAccountForm from "$lib/ui/Layout/Landing/Register/AddAccountForm.svelte";
    import Accounts from "$lib/ui/Layout/Landing/Register/Accounts.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Landing/Register.svelte";
    import Language from "./Welcome/Language.svelte";
    import Theme from "./Welcome/Language.svelte";

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
                ? Accounts
                : AddAccountForm,
        );
    };
</script>

<div class="alert-container" id="info-change-alert-container"></div>
<Form onsubmit={saveInitialPreferences}>
    <Language />
    <Theme />
    <div class="landing-body-footer">
        <Button.Basic type="submit" class="btn-cta">Continue</Button.Basic>
    </div>
</Form>
