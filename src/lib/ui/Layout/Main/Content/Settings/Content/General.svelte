<script lang="ts">
    import Autostart from "./General/Autostart.svelte";
    import AutoUpdate from "./General/AutoUpdate.svelte";
    import Language from "./General/Language.svelte";
</script>

<div class="settings-content-header">
    <h1 class="settings-content-title">General</h1>
    <span class="settings-content-description muted">These are general settings for your application.</span>
</div>
<div class="settings-content-body">
    <Autostart />
    <AutoUpdate />
    <Language />
</div>
