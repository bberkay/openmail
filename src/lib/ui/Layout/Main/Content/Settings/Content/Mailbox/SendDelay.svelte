<script lang="ts">
    import { AppController } from "$lib/controllers/AppController";
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
        AppController.changeSendDelay(newSendDelayStatus);
    }

    function resetSendDelay() {
        AppController.resetSendDelay();
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
