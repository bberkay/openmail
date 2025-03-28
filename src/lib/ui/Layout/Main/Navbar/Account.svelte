<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress, isStandardFolder } from "$lib/utils";
    import Inbox from "$lib/ui/Layout/Main/Content/Inbox.svelte";
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
        SharedStore.currentFolder = Folder.Inbox;
        SharedStore.currentAccount =
            emailAddressOrHome === "home"
                ? emailAddressOrHome
                : SharedStore.accounts.find(
                      (account: Account) =>
                          account.email_address === emailAddressOrHome,
                  )!;

        const nonInboxAccounts: Account[] = [];
        const mailboxesToCheck = emailAddressOrHome === "home"
            ? SharedStore.mailboxes
            : [emailAddressOrHome]
        for (const emailAddr in mailboxesToCheck) {
            if (
                isStandardFolder(SharedStore.mailboxes[emailAddr].folder, Folder.Inbox)
            ) {
                nonInboxAccounts.push(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddr,
                    )!,
                );
            }
        }

        if (nonInboxAccounts.length >= 1) {
            const response = await MailboxController.getMailboxes(
                nonInboxAccounts,
                Folder.Inbox,
            );
            if (!response.success) {
                showMessage({
                    content: "Error, account could not set.",
                });
                console.error(response.message);
                return;
            }
        }

        if (emailAddressOrHome === "home") {
            SharedStore.currentMailbox.folder = Folder.Inbox;
            Object.values(SharedStore.mailboxes).forEach((mailbox) => {
                SharedStore.currentMailbox.total += mailbox.total;
                SharedStore.currentMailbox.emails.prev.push(...mailbox.emails.prev);
                SharedStore.currentMailbox.emails.current.push(...mailbox.emails.current);
                SharedStore.currentMailbox.emails.next.push(...mailbox.emails.next);
            });
            Object.values(SharedStore.currentMailbox.emails).forEach((emails) => {
                emails.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
            })
        } else {
            SharedStore.currentMailbox = SharedStore.mailboxes[(SharedStore.currentAccount as Account).email_address];
        }
        showContent(Inbox);
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
