<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import {
        addEmailToAddressList,
    } from "$lib/utils";
    import * as Input from "$lib/ui/Components/Input";
    import * as Button from "$lib/ui/Components/Button";
    import Label from "$lib/ui/Components/Label";
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import { type ComposeContext } from "../Compose.svelte";
    import { getContext } from "svelte";

    interface Props {
        bccList: string[];
    }

    let { bccList = $bindable() }: Props = $props();

    let bccInput: HTMLInputElement | undefined = $state(undefined);
    const flagDraftAsChanged = getContext<ComposeContext>("compose").flagDraftAsChanged;

    const addBcc = (e: Event) => {
        addEmailToAddressList(e, bccInput!, bccList);
        flagDraftAsChanged();
    };
</script>

<FormGroup>
    <Collapse title="Bcc (optional)" class="compose-collapse bcc-compose-collapse">
        <Input.Group>
            <Input.Basic
                type="email"
                id="bcc"
                placeholder={local
                    .add_email_address_with_space_placeholder[
                    DEFAULT_LANGUAGE
                ]}
                onkeyup={addBcc}
                onblur={addBcc}
                bind:element={bccInput}
            />
            <Button.Basic type="button" onclick={addBcc}>
                <Icon name="add" />
            </Button.Basic>
        </Input.Group>
    </Collapse>
    <div class="tags">
        {#each bccList as bccAddr}
            <Badge
                content={bccAddr}
                righticon="close"
                onclick={() => {
                    bccList = bccList.filter((addr) => addr !== bccAddr);
                }}
            />
        {/each}
    </div>
</FormGroup>

<style>
    :global {
        .bcc-compose-collapse {
            margin-top: -10px;
        }
    }
</style>
