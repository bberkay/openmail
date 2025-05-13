<script lang="ts">
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ToggleSwitch } from "$lib/ui/Components/Input";
    import { onMount } from "svelte";

    let newSendDelayStatus = $state(SharedStore.preferences.isSendDelayEnabled);

    onMount(() => {
        document.removeEventListener("preferencesSaved", saveSendDelayChange);
        document.addEventListener("preferencesSaved", saveSendDelayChange);
        document.removeEventListener("preferencesResetToDefault", resetSendDelay);
        document.addEventListener("preferencesResetToDefault", resetSendDelay);
    });

    function saveSendDelayChange() {
        SharedStore.preferences.isSendDelayEnabled = newSendDelayStatus;
    }

    function resetSendDelay() {
        newSendDelayStatus = DEFAULT_PREFERENCES.isSendDelayEnabled;
        saveSendDelayChange();
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Send delay</span>
        <small class="muted">Change your send delay settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch bind:checked={newSendDelayStatus}/>
    </div>
</div>
