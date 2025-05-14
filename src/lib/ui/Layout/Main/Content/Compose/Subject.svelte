<script lang="ts">
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import * as Input from "$lib/ui/Components/Input";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { onMount } from "svelte";
    import type { OriginalMessageContext } from "$lib/types";
    import { getContext } from "svelte";
    import { type ComposeContext } from "../Compose.svelte";

    interface Props {
        value?: string;
        originalMessageContext?: OriginalMessageContext;
    }

    let { value = $bindable(), originalMessageContext }: Props = $props();

    let subjectInput: HTMLInputElement | undefined = $state(undefined);

    onMount(() => {
        if (originalMessageContext) {
            value =
                (originalMessageContext.composeType == "reply"
                    ? "Re: "
                    : "Fwd: ") + originalMessageContext.subject;
        }
    });
    const onChange = () => {
        getContext<ComposeContext>("compose").flagDraftAsChanged();
    };
</script>

<FormGroup>
    <Label for="subject">{local.subject[DEFAULT_LANGUAGE]}</Label>
    <Input.Basic
        type="text"
        name="subject"
        id="subject"
        bind:element={subjectInput}
        placeholder={local.subject_placeholder[DEFAULT_LANGUAGE]}
        bind:value
        onkeyup={onChange}
        required
    />
</FormGroup>
