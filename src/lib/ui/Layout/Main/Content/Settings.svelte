<script lang="ts">
    import Menu from "./Settings/Menu.svelte";
    import Content from "./Settings/Content.svelte";
    import General from "./Settings/Content/General.svelte";
    import Form from "$lib/ui/Components/Form";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { FileSystem } from "$lib/services/FileSystem";

    const saveChanges = async (e: Event): Promise<void> => {
        const fileSystem = await FileSystem.getInstance();
        await fileSystem.savePreferences(SharedStore.preferences);
        document.dispatchEvent(new CustomEvent("preferencesSaved"));
    };
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
    :global {
        .settings {
            width: 80%;
            height: 100%;
        }
    }
</style>
