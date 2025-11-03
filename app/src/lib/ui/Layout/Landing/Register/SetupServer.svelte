<script lang="ts">
    import { onMount } from "svelte";
    import Form from "$lib/ui/Components/Form";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showAlert } from "$lib/ui/Components/Alert";
    import { showThis as showContent } from "$lib/ui/Layout/Landing/Register.svelte";
    import Welcome from "$lib/ui/Layout/Landing/Register/Welcome.svelte";
    import { FormGroup } from "$lib/ui/Components/Form";
    import Label from "$lib/ui/Components/Label";
    import { PreferenceManager } from "$lib/preferences";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE, SERVER_URL } from "$lib/constants";
    import * as Input from "$lib/ui/Components/Input";
    import { show as showMessage } from "$lib/ui/Components/Message";

    onMount(() => {
        showAlert("info-change-alert-container", {
            content: "You can change this later.",
            type: "info",
        });
    });

    const saveInitialPreferences = async (e: Event): Promise<void> => {
        await PreferenceManager.savePreferences();
        showContent(Welcome);
    };

    const changeServerURL = async (e: Event): Promise<void> => {
        const form = e.target as HTMLFormElement;
        const formData = new FormData(form);

        const targetServerURL = formData.get("server_url") as string;
        const response = await PreferenceManager.changeServerURL(targetServerURL);

        if (!response) {
            showMessage({ title: local.error_change_server_url[DEFAULT_LANGUAGE] });
            console.error("Could not connect to the target server ", targetServerURL);
        } else {
            await saveInitialPreferences(e);
        }
    }
</script>

<div class="alert-container" id="info-change-alert-container"></div>

<Form onsubmit={changeServerURL}>
    <FormGroup>
        <Label for="server_url">
            {local.server_url[DEFAULT_LANGUAGE]}
        </Label>
        <Input.Basic
            type="url"
            name="server_url"
            id="server_url"
            placeholder={local.server_url_example[DEFAULT_LANGUAGE]}
            value={SERVER_URL}
            autocomplete="off"
            autofocus
            required
        />
    </FormGroup>

    <div class="landing-body-footer">
        <Button.Basic type="submit" class="btn-cta">Continue</Button.Basic>
    </div>
</Form>
