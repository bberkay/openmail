<script lang="ts">
    import { local } from "$lib/locales";
    import {
        DEFAULT_LANGUAGE,
    } from "$lib/constants";
    import * as Select from "$lib/ui/Components/Select";
    import Label from "$lib/ui/Components/Label";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import { createSenderAddress } from "$lib/utils";
    import { getSenderAddressTemplate } from "$lib/templates";

    interface Props {
        senderAccount: Account;
    }

    let { senderAccount = $bindable() }: Props = $props();

    const setSenderAccount = (email_address: string) => {
        senderAccount = SharedStore.accounts.find(
            (acc) => acc.email_address === email_address,
        )!;
    };
</script>

<FormGroup>
    <Label for="sender">{local.sender_s[DEFAULT_LANGUAGE]}</Label>
    <Select.Root
        id="sender"
        style="width:100%"
        placeholder={local.account[DEFAULT_LANGUAGE]}
        value={senderAccount.email_address}
        onchange={setSenderAccount}
    >
        {#each SharedStore.accounts as account}
            <Select.Option
                value={account.email_address}
                content={getSenderAddressTemplate(
                    account.email_address,
                    account.fullname,
                )}
            />
        {/each}
    </Select.Root>
</FormGroup>
