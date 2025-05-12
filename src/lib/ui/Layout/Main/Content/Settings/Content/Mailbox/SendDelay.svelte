<script lang="ts">
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

    const saveSendDelayChange = () => {
        SharedStore.preferences.isSendDelayEnabled = newSendDelayStatus;
    }

    const resetSendDelay = () => {
        newSendDelayStatus = SharedStore.preferences.isSendDelayEnabled;
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
