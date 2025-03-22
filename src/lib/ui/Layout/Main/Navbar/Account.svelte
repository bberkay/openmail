<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress } from "$lib/utils";

    type OperationType = "home" | "minimize" | "settings" | "logout" | "quit";

    const OPERATIONS: Record<OperationType, string> = {
        home: "Home",
        minimize: "Minimize to tray",
        settings: "Settings",
        logout: `Logout from ${SharedStore.currentAccount.fullname || SharedStore.currentAccount.email_address}`,
        quit: "Quit",
    };

    function setCurrentAccount(selectedAccountEmailAddr: string) {
        const selectedAccount = SharedStore.accounts.find(
            (account: Account) =>
                account.email_address === selectedAccountEmailAddr,
        )!;

        SharedStore.currentAccount = selectedAccount;
        SharedStore.currentFolder = Folder.Inbox;
    }

    function showHome() {

    }

    function minimize() {

    }

    function showSettings() {

    }

    function logout() {

    }

    function quit() {

    }

    function handleOperation(selectedOperation: OperationType | string) {
        switch (selectedOperation) {
            case "home":
                showHome();
                break;
            case "minimize":
                minimize();
                break;
            case "settings":
                showSettings();
                break;
            case "logout":
                logout();
                break;
            case "quit":
                quit();
                break;
            default:
                // if selectedOperation is none of the above, then it
                // must be an email address.
                setCurrentAccount(selectedOperation);
                break;
        }
    }
</script>

<Select.Root
    onchange={handleOperation}
    value={SharedStore.currentAccount!.email_address}
    placeholder="Account"
    enableSearch={true}
>
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>
            {createSenderAddress(account.email_address, account.fullname)}
        </Select.Option>
    {/each}
    <Select.Separator />
    {#each Object.entries(OPERATIONS) as operation}
        <Select.Option value={operation[0]}>{operation[1]}</Select.Option>
    {/each}
</Select.Root>
