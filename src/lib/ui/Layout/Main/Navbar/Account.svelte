<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Elements/Select";

    const handleAccount = (selectedAccountEmailAddr: string | null) => {
        if (selectedAccountEmailAddr) {
            const selectedAccount = SharedStore.accounts.find((account: Account) => account.email_address === selectedAccountEmailAddr);
            if (!selectedAccount) {
                alert("Selected account could not found");
                return;
            }

            SharedStore.currentAccount = selectedAccount || null;
            SharedStore.currentFolder = Folder.Inbox;
        }
    }
</script>

<Select.Menu onchange={handleAccount} value={SharedStore.currentAccount?.email_address} placeholder="Account">
    <Select.Option value="">Home</Select.Option>
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>{account.fullname} &lt;{account.email_address}&gt;</Select.Option>
    {/each}
</Select.Menu>
