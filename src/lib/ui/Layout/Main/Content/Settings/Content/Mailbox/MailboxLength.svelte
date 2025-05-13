<script lang="ts">
    import { DEFAULT_PREFERENCES } from "$lib/constants";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxLength } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { getEnumKeyByValue } from "$lib/utils";
    import { onMount } from "svelte";

    let newMailboxLength: MailboxLength = $state(SharedStore.preferences.mailboxLength);

    onMount(() => {
        document.removeEventListener("preferencesSaved", saveMailboxLengthChange);
        document.addEventListener("preferencesSaved", saveMailboxLengthChange);
        document.removeEventListener("preferencesResetToDefault", resetMailboxLength);
        document.addEventListener("preferencesResetToDefault", resetMailboxLength);
    });

    async function saveMailboxLengthChange() {
        SharedStore.preferences.mailboxLength = newMailboxLength;
        await MailboxController.init();
    }

    async function resetMailboxLength() {
        newMailboxLength = DEFAULT_PREFERENCES.mailboxLength;
        await saveMailboxLengthChange();
    }

    const updateMailboxLength = (selectedLength: string) => {
        newMailboxLength = Number(selectedLength) as MailboxLength;
    };
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Mailbox Length</span>
        <small class="muted">Change your mailbox length</small>
    </div>
    <div class="settings-section-body">
        <Select.Root
            id="language"
            class="select-sm"
            placeholder="Language"
            value={getEnumKeyByValue(
                MailboxLength,
                SharedStore.preferences.mailboxLength,
            )}
            onchange={updateMailboxLength}
            disableClearButton={true}
        >
            {#each Object.entries(MailboxLength) as [mailboxLengthName, mailboxLengthId]}
                <Select.Option
                    value={mailboxLengthId.toString()}
                    content={mailboxLengthName}
                />
            {/each}
        </Select.Root>
    </div>
</div>
