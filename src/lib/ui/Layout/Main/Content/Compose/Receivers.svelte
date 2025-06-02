<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import {
        addEmailToAddressList,
        extractEmailAddress,
    } from "$lib/utils";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import Icon from "$lib/ui/Components/Icon";
    import { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import type { OriginalMessageContext } from "$lib/types";
    import { getContext, onMount } from "svelte";
    import { type ComposeContext } from "../Compose.svelte";

    interface Props {
        receiverList: string[];
        originalMessageContext?: OriginalMessageContext;
    }

    let {
        receiverList = $bindable(),
        originalMessageContext
    }: Props = $props();

    let receiverInput: HTMLInputElement | undefined = $state(undefined);
    const flagDraftAsChanged = getContext<ComposeContext>("compose").flagDraftAsChanged;

    onMount(() => {
        if (originalMessageContext) {
            receiverList = originalMessageContext.receivers
                  .split(",")
                  .map((receiver) => extractEmailAddress(receiver));
        };
    });

    const addReceiver = (e: Event) => {
        addEmailToAddressList(e, receiverInput!, receiverList);
        flagDraftAsChanged();
    };
</script>

<FormGroup>
    <Label for="receivers">
        {local.receiver_s[DEFAULT_LANGUAGE]}
    </Label>
    <Input.Group>
        <Input.Basic
            type="email"
            id="receivers"
            placeholder={local
                .add_email_address_with_space_placeholder[
                DEFAULT_LANGUAGE
            ]}
            onkeyup={addReceiver}
            onblur={addReceiver}
            bind:element={receiverInput}
        />
        <Button.Basic type="button" onclick={addReceiver}>
            <Icon name="add" />
        </Button.Basic>
    </Input.Group>
    <div class="tags">
        {#each receiverList as receiver}
            <Badge
                content={receiver}
                righticon="close"
                onclick={() => {
                    receiverList = receiverList.filter(
                        (addr) => addr !== receiver,
                    );
                }}
            />
        {/each}
    </div>
</FormGroup>
