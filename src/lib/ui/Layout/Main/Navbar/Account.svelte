<script lang="ts">
    import { exit } from "@tauri-apps/plugin-process";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { type Account } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
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
    import AccountSelection, { setCurrentAccount } from "$lib/ui/Layout/Main/Portable/AccountSelection.svelte";

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

    const handleShortcuts = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
            e.preventDefault();
            isAccountSelectionHidden = true;
        }
    };
</script>

<svelte:window onkeydown={handleShortcuts} />

<Dropdown.Root class="accounts">
    <Dropdown.Toggle>
        {SharedStore.currentAccount === "home"
            ? local.home[DEFAULT_LANGUAGE]
            : SharedStore.currentAccount.email_address}
    </Dropdown.Toggle>
    <Dropdown.Content>
        <Dropdown.Item onclick={setCurrentAccountToHome}>
            {local.home[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Item onclick={showAccountSelection}>
            Change account
        </Dropdown.Item>
        <Dropdown.Separator/>
        <Dropdown.Item onclick={minimize}>
            {local.minimize_to_tray[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Item onclick={showSettings}>
            {local.settings[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        {#if SharedStore.currentAccount !== "home"}
            <Dropdown.Item onclick={logout}>
                {getLogoutFromTemplate(
                    SharedStore.currentAccount.fullname ||
                        SharedStore.currentAccount.email_address,
                )}
            </Dropdown.Item>
        {/if}
        <Dropdown.Item onclick={quit}>
            {local.quit[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
    </Dropdown.Content>
</Dropdown.Root>

<AccountSelection
    bind:isAccountSelectionHidden
    allowMultipleSelection={false}
    actionOnSelect={setCurrentAccount}
    initialSelectedAccounts={SharedStore.currentAccount}
/>
