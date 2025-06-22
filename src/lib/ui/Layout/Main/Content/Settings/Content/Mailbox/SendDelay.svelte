<script lang="ts">
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ToggleSwitch } from "$lib/ui/Components/Input";
    import { onMount } from "svelte";

    let newSendDelayStatus = $state(SharedStore.preferences.isSendDelayEnabled);

    onMount(() => {
        document.removeEventListener("preferences-saved", saveSendDelayChange);
        document.addEventListener("preferences-saved", saveSendDelayChange);
        document.removeEventListener("preferences-reset-to-default", resetSendDelay);
        document.addEventListener("preferences-reset-to-default", resetSendDelay);
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
