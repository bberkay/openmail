<script lang="ts">
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ToggleSwitch } from "$lib/ui/Components/Input";
    import { enable, isEnabled, disable } from '@tauri-apps/plugin-autostart';
    import { onMount } from "svelte";

    let newAutostartStatus = $state(SharedStore.preferences.isAutostartEnabled);

    onMount(() => {
        document.removeEventListener("preferencesSaved", saveAutostartChange);
        document.addEventListener("preferencesSaved", saveAutostartChange);
        document.removeEventListener("preferencesResetToDefault", resetAutostart);
        document.addEventListener("preferencesResetToDefault", resetAutostart);
    });

    async function saveAutostartChange() {
        // Set new status
        SharedStore.preferences.isAutostartEnabled = newAutostartStatus;
        if (newAutostartStatus) {
            await enable();
        } else {
            disable();
        }

        // Check again to make sure and show if it is really enabled/disabled.
        SharedStore.preferences.isAutostartEnabled = await isEnabled();
        newAutostartStatus = SharedStore.preferences.isAutostartEnabled;
    }

    async function resetAutostart() {
        newAutostartStatus = DEFAULT_PREFERENCES.isAutostartEnabled;
        await saveAutostartChange();
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Autostart</span>
        <small class="muted">Change your autostart settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch bind:checked={newAutostartStatus}/>
    </div>
</div>
