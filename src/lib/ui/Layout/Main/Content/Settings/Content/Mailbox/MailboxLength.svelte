<script lang="ts">
    import { PreferenceManager, PreferenceStore } from "$lib/preferences";
    import { MailboxLength } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { getEnumKeyByValue } from "$lib/utils";

    const changeMailboxLength = async (selectedLength: string) => {
        await PreferenceManager.changeMailboxLength(selectedLength as MailboxLength);
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
                PreferenceStore.mailboxLength,
            )}
            onchange={changeMailboxLength}
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
