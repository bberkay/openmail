<script lang="ts">
    import { PreferenceManager } from "$lib/managers/PreferenceManager";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";
    import { ToggleSwitch } from "$lib/ui/Components/Input";

    const changeAutostart = async (newAutostartStatus: boolean) => {
        await PreferenceManager.changeAutostart(newAutostartStatus);
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Autostart</span>
        <small class="muted">Change your autostart settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch
            onchange={changeAutostart}
            checked={PreferencesStore.isAutostartEnabled}
        />
    </div>
</div>
