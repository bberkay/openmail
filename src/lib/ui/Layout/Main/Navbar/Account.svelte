<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress } from "$lib/utils";
    import { show as showMessage } from "$lib/ui/Components/Message";

    const mailboxController = new MailboxController();

    const handleAccount = (selectedAccountEmailAddr: string | null) => {
        if (selectedAccountEmailAddr) {
            const selectedAccount = SharedStore.accounts.find(
                (account: Account) => account.email_address === selectedAccountEmailAddr
            );
            if (!selectedAccount) {
                showMessage({content: "Selected account could not found"});
                return;
            }

            SharedStore.currentAccount = selectedAccount || null;
            SharedStore.currentFolder = Folder.Inbox;
            mailboxController.init(SharedStore.currentAccount);
        }
    }
</script>

<Select.Root
    onchange={handleAccount}
    value={SharedStore.currentAccount?.email_address}
    placeholder="Account"
>
    <Select.Option value="">Home</Select.Option>
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>
            {createSenderAddress(account.email_address, account.fullname)}
        </Select.Option>
    {/each}
</Select.Root>
