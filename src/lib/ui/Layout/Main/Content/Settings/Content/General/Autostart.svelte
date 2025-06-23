<script lang="ts">
    import { AppController } from "$lib/controllers/AppController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { ToggleSwitch } from "$lib/ui/Components/Input";
    import { onMount } from "svelte";

    let newAutostartStatus = $state(SharedStore.preferences.isAutostartEnabled);

    onMount(() => {
        document.removeEventListener("preferences-saved", saveAutostartChange);
        document.addEventListener("preferences-saved", saveAutostartChange);
        document.removeEventListener(
            "preferences-reset-to-default",
            resetAutostart,
        );
        document.addEventListener("preferences-reset-to-default", resetAutostart);
    });

    async function saveAutostartChange() {
        await AppController.changeAutostart(newAutostartStatus);
    }

    async function resetAutostart() {
        await AppController.resetAutostart();
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Autostart</span>
        <small class="muted">Change your autostart settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch bind:checked={newAutostartStatus} />
    </div>
</div>
