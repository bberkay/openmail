<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress, isStandardFolder } from "$lib/utils";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";

    const AccountOperation = {
        Home: "create",
        Minimize: "refresh",
        Settings: "settings",
        Logout: "logout",
        Quit: "quit",
    } as const;

    const setCurrentAccount = async (
        emailAddressOrHome: "home" | string,
    ): Promise<void> => {
        const newAccount =
            emailAddressOrHome === "home"
                ? emailAddressOrHome
                : SharedStore.accounts.find(
                      (account: Account) =>
                          account.email_address === emailAddressOrHome,
                  )!;

        if (SharedStore.currentAccount === newAccount)
            return;

        SharedStore.currentAccount = newAccount;

        const nonInboxAccounts: Account[] = [];
        const mailboxesToCheck = SharedStore.currentAccount === "home"
            ? Object.keys(SharedStore.mailboxes)
            : [SharedStore.currentAccount.email_address]
        for (const emailAddr in mailboxesToCheck) {
            if (
                !isStandardFolder(SharedStore.mailboxes[emailAddr].folder, Folder.Inbox)
            ) {
                nonInboxAccounts.push(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddr,
                    )!,
                );
            }
        }

        if (nonInboxAccounts.length >= 1) {
            nonInboxAccounts.forEach(async (account) => {
                const response = await MailboxController.getMailbox(
                    account,
                    Folder.Inbox,
                );
                if (!response.success) {
                    showMessage({
                        content: `Error, inbox of ${account.email_address} could not retrived.`,
                    });
                    console.error(response.message);
                    return;
                }
            })
        }

        showContent(Mailbox);
    };

    const minimize = () => {};

    const showSettings = () => {};

    const logout = () => {};

    const quit = () => {};

    const handleOperation = (selectedOperation: string) => {
        switch (selectedOperation) {
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
