<script lang="ts">
    import { onMount } from "svelte";
    import * as Input from "$lib/ui/Components/Input";
    import { getMailboxContext } from "$lib/ui/Layout/Main/Content/Mailbox";

    const mailboxContext = getMailboxContext();

    let selectShownCheckbox: HTMLInputElement;
    let shownEmailUids: string[] = [];
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    $effect(() => {
        if (mailboxContext.getCurrentMailbox()) {
            shownEmailUids = [];
            document
                .querySelectorAll<HTMLInputElement>(
                    ".mailbox .email-preview-selection",
                )
                .forEach((element) => {
                    shownEmailUids.push(element.value);
                });
        }

        if (
            mailboxContext.emailSelection.value.length < 2 &&
            selectShownCheckbox
        ) {
            selectShownCheckbox.checked = false;
        }
    });

    const selectShownEmails = () => {
        mailboxContext.emailSelection.value = selectShownCheckbox.checked
            ? shownEmailUids
            : [];
    };
</script>

<div class="tool">
    <Input.Basic
        type="checkbox"
        id="select-shown"
        onclick={selectShownEmails}
    />
</div>
