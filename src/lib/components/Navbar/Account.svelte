<script lang="ts">
    import Select from "$lib/components/Elements/Select.svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Option from "$lib/components/Elements/Option.svelte";
    import { Folder } from "$lib/types";

    const handleAccount = (selectedAccountEmailAddr: string | null) => {
        if (selectedAccountEmailAddr) {
            const selectedAccount = SharedStore.accounts.find(account => account.email_address === selectedAccountEmailAddr);
            if (!selectedAccount) {
                alert("Selected account could not found");
                return;
            }

            SharedStore.currentAccount = selectedAccount;
            SharedStore.currentFolder = Folder.Inbox;
        }
    }
</script>

<Select onchange={handleAccount} value={SharedStore.currentAccount?.email_address} placeholder="Account">
    {#each SharedStore.accounts as account}
        <Option value={account.email_address}>{account.fullname} &lt;{account.email_address}&gt;</Option>
    {/each}
</Select>
