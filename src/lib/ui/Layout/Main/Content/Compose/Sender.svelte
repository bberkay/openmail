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

    interface Props {
        senderAccount: Account;
    }

    let { senderAccount = $bindable() }: Props = $props();

    const setSenderAccount = (senderEmailAddr: string) => {
        senderAccount = SharedStore.accounts.find(
            (acc) => acc.email_address === senderEmailAddr,
        )!;
    };
</script>

<FormGroup>
    <Label for="sender">{local.sender_s[DEFAULT_LANGUAGE]}</Label>
    <Select.Root
        id="sender"
        placeholder={local.account[DEFAULT_LANGUAGE]}
        onchange={setSenderAccount}
    >
        {#each SharedStore.accounts as account}
            {@const sender = createSenderAddress(
                account.email_address,
                account.fullname,
            )}
            <Select.Option value={sender} content={sender} />
        {/each}
    </Select.Root>
</FormGroup>
