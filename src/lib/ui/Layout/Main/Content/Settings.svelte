<script lang="ts">
    import Menu from "./Settings/Menu.svelte";
    import Content, { backToDefault as showDefaultSettings } from "./Settings/Content.svelte";
    import General from "./Settings/Content/General.svelte";
    import Form from "$lib/ui/Components/Form";
    import { onMount } from "svelte";
    import { PreferenceManager } from "$lib/managers/PreferenceManager";

    const saveChanges = async (): Promise<void> => {
        await PreferenceManager.savePreferences();
    };

    onMount(() => {
        showDefaultSettings();
    })
</script>

<div class="settings">
    <Form onsubmit={saveChanges} style="height:100%;">
        <Menu />
        <Content>
            <General />
        </Content>
    </Form>
</div>

<style>
    .settings {
        width: 80%;
        height: 100%;
    }
</style>
