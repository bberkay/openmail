<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress } from "$lib/utils";

    const AccountOperation = {
        Home: "create",
        Minimize: "refresh",
        Settings: "settings",
        Logout: "logout",
        Quit: "quit",
    } as const;

    const setCurrentAccount = (selectedAccountEmailAddr: string) => {
        const selectedAccount = SharedStore.accounts.find(
            (account: Account) =>
                account.email_address === selectedAccountEmailAddr,
        )!;

        SharedStore.currentAccount = selectedAccount;
        SharedStore.currentFolder = Folder.Inbox;
    };

    const showHome = () => {
        SharedStore.currentAccount = "home";
        SharedStore.currentFolder = Folder.Inbox;
    };

    const minimize = () => {};

    const showSettings = () => {};

    const logout = () => {};

    const quit = () => {};

    const handleOperation = (selectedOperation: string) => {
        switch (selectedOperation) {
            case AccountOperation.Home:
                showHome();
                break;
            case AccountOperation.Minimize:
                minimize();
                break;
            case AccountOperation.Settings:
                showSettings();
                break;
            case AccountOperation.Logout:
                logout();
                break;
            case AccountOperation.Quit:
                quit();
                break;
            default:
                // if selectedOperation is none of the above, then it
                // must be an email address.
                setCurrentAccount(selectedOperation);
                break;
        }
    };
</script>

<Select.Root
    onchange={handleOperation}
    value={SharedStore.currentAccount === "home"
        ? "Home"
        : SharedStore.currentAccount.email_address}
    placeholder="Account"
    enableSearch={true}
>
    <Select.Option value={AccountOperation.Home}>Home</Select.Option>
    <Select.Separator />
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>
            {createSenderAddress(account.email_address, account.fullname)}
        </Select.Option>
    {/each}
    <Select.Separator />
    <Select.Option value={AccountOperation.Minimize}>
        Minimize to tray
    </Select.Option>
    <Select.Option value={AccountOperation.Settings}>Settings</Select.Option>
    {#if SharedStore.currentAccount !== "home"}
        <Select.Option value={AccountOperation.Logout}>
            Logout from
            {SharedStore.currentAccount.fullname ||
                SharedStore.currentAccount.email_address}
        </Select.Option>
    {/if}
    <Select.Option value={AccountOperation.Quit}>Quit</Select.Option>
</Select.Root>
