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
    import Icon from "$lib/ui/Components/Icon";
    import Collapse from "$lib/ui/Components/Collapse";
    import { FormGroup } from "$lib/ui/Components/Form";
    import Badge from "$lib/ui/Components/Badge";
    import { getContext } from "svelte";
    import { type ComposeContext } from "../Compose.svelte";

    interface Props {
        ccList: string[];
    }

    let { ccList = $bindable() }: Props = $props();

    let ccInput: HTMLInputElement | undefined = $state(undefined);
    const flagDraftAsChanged = getContext<ComposeContext>("compose").flagDraftAsChanged;

    const addCc = (e: Event) => {
        addEmailToAddressList(e, ccInput!, ccList);
        flagDraftAsChanged();
    };
</script>

<FormGroup>
    <Collapse title="Cc (optional)" class="compose-collapse">
        <Input.Group>
            <Input.Basic
                type="email"
                id="cc"
                placeholder={local
                    .add_email_address_with_space_placeholder[
                    DEFAULT_LANGUAGE
                ]}
                onkeyup={addCc}
                onblur={addCc}
                bind:element={ccInput}
            />
            <Button.Basic type="button" onclick={addCc}>
                <Icon name="add" />
            </Button.Basic>
        </Input.Group>
    </Collapse>
    <div class="tags">
        {#each ccList as ccAddr}
            <Badge
                content={ccAddr}
                righticon="close"
                onclick={() => {
                    ccList = ccList.filter((addr) => addr !== ccAddr);
                }}
            />
        {/each}
    </div>
</FormGroup>

<style>
    :global {
        .compose {
            & .compose-collapse {
                margin-bottom: 0;

                & .collapse-header {
                    padding: 0 1px;
                    padding-right: var(--spacing-2xs);
                }

                & .header-content {
                    font-size: var(--font-size-sm);
                }

                & .collapse-content {
                    padding: 0;
                }
            }
        }
    }
</style>
