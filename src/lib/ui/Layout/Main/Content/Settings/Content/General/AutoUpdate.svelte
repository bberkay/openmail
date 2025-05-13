<script lang="ts">
    import * as Button from "$lib/ui/Components/Button";
    import { ToggleSwitch } from "$lib/ui/Components/Input";

    // TODO: Implement this after updater plugin is added.
    const checkForUpdates = () => {

    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Auto Update</span>
        <small class="muted">Change your autoupdate settings</small>
    </div>
    <div class="settings-section-body">
        <ToggleSwitch />
    </div>
</div>
<div class="settings-section">
    <div class="settings-section-title">
        <span>Check for updates</span>
        <small class="muted">Change your autoupdate settings</small>
    </div>
    <div class="settings-section-body">
        <Button.Action
            type="button"
            class="btn-outline btn-md"
            onclick={checkForUpdates}
        >
            Update if available
        </Button.Action>
    </div>
</div>
