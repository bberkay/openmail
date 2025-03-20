<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress } from "$lib/utils";

    const setCurrentAccount = async (selectedAccountEmailAddr: string) => {
        const selectedAccount = SharedStore.accounts.find(
            (account: Account) => account.email_address === selectedAccountEmailAddr
        )!;

        SharedStore.currentAccount = selectedAccount;
        SharedStore.currentFolder = Folder.Inbox;
    }
</script>

<Select.Root
    onchange={setCurrentAccount}
    value={SharedStore.currentAccount!.email_address}
    placeholder="Account"
>
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>
            {createSenderAddress(account.email_address, account.fullname)}
        </Select.Option>
    {/each}
</Select.Root>
