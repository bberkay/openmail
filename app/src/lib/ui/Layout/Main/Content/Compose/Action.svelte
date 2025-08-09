<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import * as Button from "$lib/ui/Components/Button";
    import Icon from "$lib/ui/Components/Icon";

    interface Props {
        isSendingEmail: boolean;
        isSavingDraft: boolean;
        saveDraft: () => Promise<void>;
        deleteDraft: () => Promise<void>;
    }

    let {
        isSendingEmail = $bindable(),
        isSavingDraft = $bindable(),
        saveDraft,
        deleteDraft
    }: Props = $props();
</script>

<div class="compose-action-container">
    <div class="compose-action-container-left">
        <Button.Action
            type="button"
            id="delete-draft"
            class="btn-inline"
            onclick={deleteDraft}
            disabled={isSendingEmail || isSavingDraft}
        >
            <Icon name="trash" />
        </Button.Action>
    </div>
    <div class="compose-action-container-right">
        <Button.Action
            type="button"
            id="save-draft"
            class="btn-outline"
            onclick={saveDraft}
            disabled={isSendingEmail || isSavingDraft}
        >
            {local.save_as_draft[DEFAULT_LANGUAGE]}
        </Button.Action>
        <Button.Basic
            type="submit"
            id="send-email"
            class="btn-cta"
            style="width:auto"
            disabled={isSendingEmail || isSavingDraft}
        >
            {local.send_email[DEFAULT_LANGUAGE]}
        </Button.Basic>
    </div>
</div>

<style>
    :global {
        .compose {
            .compose-action-container {
                display: flex;
                justify-content: space-between;
                margin-top: var(--spacing-lg);

                & .compose-action-container-right {
                    display: flex;
                    align-items: center;
                    gap: var(--spacing-md);
                }
            }
        }
    }
</style>
