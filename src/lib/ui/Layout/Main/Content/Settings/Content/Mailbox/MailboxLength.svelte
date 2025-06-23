<script lang="ts">
    import { AppController } from "$lib/controllers/AppController";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxLength } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { getEnumKeyByValue } from "$lib/utils";
    import { onMount } from "svelte";

    let newMailboxLength: MailboxLength = $state(SharedStore.preferences.mailboxLength);

    onMount(() => {
        document.removeEventListener("preferences-saved", saveMailboxLengthChange);
        document.addEventListener("preferences-saved", saveMailboxLengthChange);
        document.removeEventListener("preferences-reset-to-default", resetMailboxLength);
        document.addEventListener("preferences-reset-to-default", resetMailboxLength);
    });

    async function saveMailboxLengthChange() {
        await AppController.changeMailboxLength(newMailboxLength);
    }

    async function resetMailboxLength() {
        await AppController.resetMailboxLength();
    }

    const updateMailboxLength = (selectedLength: string) => {
        newMailboxLength = selectedLength as MailboxLength;
    };
</script>

<div class="settings-section">
    <div class="settings-section-title">
        <span>Mailbox Length</span>
        <small class="muted">Change your mailbox length</small>
    </div>
    <div class="settings-section-body">
        <span>{Object.entries(MailboxLength)}</span>
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
