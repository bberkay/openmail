<script lang="ts">
    import { PreferenceManager } from "$lib/managers/PreferenceManager";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";
    import { ToggleSwitch } from "$lib/ui/Components/Input";

    const changeSendDelay = (newSendDelayStatus: boolean) => {
        PreferenceManager.changeSendDelay(newSendDelayStatus);
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Send delay</span>
        <small class="muted">Change your send delay settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch
            onchange={changeSendDelay}
            checked={PreferencesStore.isSendDelayEnabled}
        />
    </div>
</div>
