<script lang="ts">
    import { onMount } from "svelte";
    import * as Input from "$lib/ui/Components/Input";
    import {
        getCurrentMailbox,
        type EmailSelection,
    } from "$lib/ui/Layout/Main/Content/Mailbox.svelte";

    interface Props {
        emailSelection: EmailSelection;
    }

    let { emailSelection = $bindable() }: Props = $props();

    let selectShownCheckbox: HTMLInputElement;
    let shownEmailUids: string[] = [];
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown",
        ) as HTMLInputElement;
    });

    $effect(() => {
        if (getCurrentMailbox()) {
            shownEmailUids = [];
            document
                .querySelectorAll<HTMLInputElement>(
                    ".mailbox .email-selection-checkbox",
                )
                .forEach((element) => {
                    shownEmailUids.push(element.value);
                });
        }
    });

    const selectShownEmails = () => {
        emailSelection = selectShownCheckbox.checked ? shownEmailUids : [];
    };
</script>

<div class="tool">
    <Input.Basic
        type="checkbox"
        id="select-shown"
        onclick={selectShownEmails}
    />
</div>
