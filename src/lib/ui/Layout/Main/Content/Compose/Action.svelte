<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        isSendingEmail: boolean;
        isSavingDraft: boolean;
        saveDraft: () => Promise<void>;
    }

    let {
        isSendingEmail = $bindable(),
        isSavingDraft = $bindable(),
        saveDraft
    }: Props = $props();
</script>

<div class="compose-action-container">
    <Button.Basic
        type="submit"
        id="send-email"
        class="btn-cta"
        disabled={isSendingEmail || isSavingDraft}
    >
        {local.send_email[DEFAULT_LANGUAGE]}
    </Button.Basic>
    <Button.Action
        type="button"
        id="save-draft"
        class="btn-outline"
        onclick={saveDraft}
        disabled={isSendingEmail || isSavingDraft}
    >
        {local.save_as_draft[DEFAULT_LANGUAGE]}
    </Button.Action>
</div>

<style>
    .compose-action-container {
        margin-top: var(--spacing-lg);
    }
</style>
