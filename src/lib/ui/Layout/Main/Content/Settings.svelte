<script lang="ts">
    import Menu from "./Settings/Menu.svelte";
    import Content, { backToDefault as showDefaultSettings } from "./Settings/Content.svelte";
    import General from "./Settings/Content/General.svelte";
    import Form from "$lib/ui/Components/Form";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { FileSystem } from "$lib/services/FileSystem";
    import { onMount } from "svelte";

    const saveChanges = async (): Promise<void> => {
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences(SharedStore.preferences);
        document.dispatchEvent(new CustomEvent("preferencesSaved"));
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
