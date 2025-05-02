<script lang="ts">
    import { exit } from "@tauri-apps/plugin-process";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { AccountController } from "$lib/controllers/AccountController";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import {
        getLogoutFromTemplate,
        getNotLoggedOutFromTemplate,
    } from "$lib/templates";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import AccountSelection, { setCurrentAccount } from "./Account/AccountSelection.svelte";

    const AccountOperation = {
        ShowHome: "showHome",
        ShowAccountSelection: "showAccountSelection",
        Minimize: "minimize",
        Settings: "settings",
        Logout: "logout",
        Quit: "quit",
    } as const;

    let isAccountSelectionHidden = $state(true);

    const setCurrentAccountToHome = () => {
        setCurrentAccount("home");
    }

    const showAccountSelection = () => {
        isAccountSelectionHidden = false;
    }

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
                showToast({ content: "logout success" });
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
            case AccountOperation.ShowHome:
                setCurrentAccountToHome();
                break;
            case AccountOperation.ShowAccountSelection:
                showAccountSelection();
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
                break;
        }
    };

    const handleShortcuts = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
            e.preventDefault();
            isAccountSelectionHidden = true;
        }
    };
</script>

<svelte:window onkeydown={handleShortcuts} />

<Select.Root
    class="account"
    onchange={handleOperation}
    value={SharedStore.currentAccount === "home"
        ? AccountOperation.ShowHome
        : SharedStore.currentAccount.email_address}
    placeholder={local.account[DEFAULT_LANGUAGE]}
    disableClearButton={true}
    resetAfterSelect={true}
>
    <Select.Option
        value={AccountOperation.ShowHome}
        content={local.home[DEFAULT_LANGUAGE]}
    />
    <Select.Option
        value={AccountOperation.ShowAccountSelection}
        content="Change account"
    />
    <Select.Separator />
    <Select.Option
        value={AccountOperation.Minimize}
        content={local.minimize_to_tray[DEFAULT_LANGUAGE]}
    />
    <Select.Option
        value={AccountOperation.Settings}
        content={local.settings[DEFAULT_LANGUAGE]}
    />
    {#if SharedStore.currentAccount !== "home"}
        <Select.Option
            value={AccountOperation.Logout}
            content={getLogoutFromTemplate(
                SharedStore.currentAccount.fullname ||
                    SharedStore.currentAccount.email_address,
            )}
        />
    {/if}
    <Select.Option
        value={AccountOperation.Quit}
        content={local.quit[DEFAULT_LANGUAGE]}
    />
</Select.Root>

<AccountSelection bind:isAccountSelectionHidden />

<style>
    :global {
        nav {
            & .account {
                width: 150px;
            }
        }
    }
</style>
