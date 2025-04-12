<script lang="ts">
    import { exit, relaunch } from "@tauri-apps/plugin-process";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { createSenderAddress, isStandardFolder } from "$lib/utils";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { AccountController } from "$lib/controllers/AccountController";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import {
        getLogoutFromTemplate,
        getNotLoggedOutFromTemplate,
    } from "$lib/templates";

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

        if (SharedStore.currentAccount === newAccount) return;
        SharedStore.currentAccount = newAccount;

        const nonInboxAccounts: Account[] = [];
        const mailboxesToCheck =
            SharedStore.currentAccount === "home"
                ? Object.keys(SharedStore.mailboxes)
                : [SharedStore.currentAccount.email_address];
        for (const emailAddr in mailboxesToCheck) {
            if (
                !isStandardFolder(
                    SharedStore.mailboxes[emailAddr].folder,
                    Folder.Inbox,
                )
            ) {
                nonInboxAccounts.push(
                    SharedStore.accounts.find(
                        (acc) => acc.email_address === emailAddr,
                    )!,
                );
            }
        }

        if (nonInboxAccounts.length >= 1) {
            const results = await Promise.allSettled(
                nonInboxAccounts.map(async (account) => {
                    const response = await MailboxController.getMailbox(
                        account,
                        Folder.Inbox,
                    );
                    if (!response.success) {
                        throw new Error(response.message);
                    }
                }),
            );

            const failed = results.filter((r) => r.status === "rejected");

            if (failed.length > 0) {
                showMessage({
                    title: local.error_show_home[DEFAULT_LANGUAGE],
                });
                failed.forEach((f) => console.error(f.reason));
                return;
            }
        }

        showContent(Mailbox);
    };

    const minimize = () => {};

    const showSettings = () => {};

    const logout = () => {
        showConfirm({
            title: local.are_you_certain_log_out[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_logout[DEFAULT_LANGUAGE],
            onConfirm: async () => {
                const response = await AccountController.remove(
                    (SharedStore.currentAccount as Account).email_address,
                );
                if (!response.success) {
                    showMessage({
                        title: getNotLoggedOutFromTemplate(
                            (SharedStore.currentAccount as Account)
                                .email_address,
                        ),
                    });
                    console.error(response.message);
                    return;
                }
            },
        });
    };

    const quit = () => {
        showConfirm({
            title: local.are_you_certain_quit_app[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_close_the_app[DEFAULT_LANGUAGE],
            onConfirm: async () => {
                await exit(0);
            },
        });
    };

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
        ? local.home[DEFAULT_LANGUAGE]
        : SharedStore.currentAccount.email_address}
    placeholder={local.account[DEFAULT_LANGUAGE]}
    enableSearch={true}
>
    <Select.Option value={AccountOperation.Home}>
        {local.home[DEFAULT_LANGUAGE]}
    </Select.Option>
    <Select.Separator />
    {#each SharedStore.accounts as account}
        <Select.Option value={account.email_address}>
            {createSenderAddress(account.email_address, account.fullname)}
        </Select.Option>
    {/each}
    <Select.Separator />
    <Select.Option value={AccountOperation.Minimize}>
        {local.minimize_to_tray[DEFAULT_LANGUAGE]}
    </Select.Option>
    <Select.Option value={AccountOperation.Settings}>
        {local.settings[DEFAULT_LANGUAGE]}
    </Select.Option>
    {#if SharedStore.currentAccount !== "home"}
        <Select.Option value={AccountOperation.Logout}>
            {getLogoutFromTemplate(
                SharedStore.currentAccount.fullname ||
                    SharedStore.currentAccount.email_address,
            )}
        </Select.Option>
    {/if}
    <Select.Option value={AccountOperation.Quit}>
        {local.quit[DEFAULT_LANGUAGE]}
    </Select.Option>
</Select.Root>
