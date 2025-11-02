<script lang="ts">
    import { PreferenceManager } from "$lib/preferences";
    import * as Button from "$lib/ui/Components/Button";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { relaunch } from '@tauri-apps/plugin-process';

    const resetServerURL = async () => {
        showConfirm({
            title: local.confirm_reset_server_url[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_restart[DEFAULT_LANGUAGE],
            onConfirm: async () => {
                await PreferenceManager.resetServerURL()
                await PreferenceManager.savePreferences();
                await relaunch();
            },
        });
    }
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Reset Server</span>
        <small class="muted">Change your server url</small>
    </div>
    <div class="settings-section-body">
        <Button.Basic
            type="button"
            class="btn-cta"
            style="width:auto"
            onclick={resetServerURL}
        >
            <span>Reset</span>
        </Button.Basic>
    </div>
</div>
