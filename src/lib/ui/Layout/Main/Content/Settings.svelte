<script lang="ts">
    import Menu from "./Settings/Menu.svelte";
    import Content from "./Settings/Content.svelte";
    import General from "./Settings/Content/General.svelte";
</script>

<div class="settings">
    <Menu />
    <Content>
        <General />
    </Content>
</div>

<style>
    :global {
        .settings {
            width: 80%;
        }
    }
</style>
