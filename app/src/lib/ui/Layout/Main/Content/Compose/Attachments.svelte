<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import * as Input from "$lib/ui/Components/Input";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { onMount } from "svelte";
    import { triggerDraftChange } from "../Compose.svelte";

    let attachments: HTMLInputElement | undefined = $state();
    onMount(() => {
        attachments!.addEventListener("change", () => {
            triggerDraftChange();
        })
    })
</script>

<FormGroup>
    <Label for="attachments">
        {local.attachment_s[DEFAULT_LANGUAGE]}
    </Label>
    <Input.File
        name="attachments"
        id="attachments"
        class="attachments"
        bind:element={attachments}
        multiple
        />
</FormGroup>

<style>
    :global {
        .compose {
            .attachments {
                margin-top: var(--spacing-xs);
                width: 100%;
            }
        }
    }
</style>
