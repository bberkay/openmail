<script lang="ts">
    import { exit } from "@tauri-apps/plugin-process";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { show as showModal } from "$lib/ui/Components/Modal";
    import Settings from "$lib/ui/Layout/Main/Content/Settings.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import {
        getNotLoggedOutFromTemplate,
    } from "$lib/templates";
    import { show as showToast } from "$lib/ui/Components/Toast";
    import AccountSelection, { setCurrentAccount } from "./Account/AccountSelection.svelte";
    import { type Account } from "$lib/types";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { createSenderAddressFromAccount } from "$lib/utils";
    import { show as showTooltip } from "$lib/ui/Components/Tooltip";

    const setCurrentAccountAsHome = async () => {
        await setCurrentAccount("home");
    }

    const showAccountSelection = () => {
        showModal(AccountSelection);
    }

    const showSettings = () => {
        showContent(Settings);
    };

    const minimize = () => {};

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
</script>

<Dropdown.Root class="accounts">
    <Dropdown.Toggle>
        <span use:showTooltip>
            {SharedStore.currentAccount === "home"
                ? local.home[DEFAULT_LANGUAGE]
                : SharedStore.currentAccount.email_address}
        </span>
    </Dropdown.Toggle>
    <Dropdown.Content>
        <Dropdown.Item onclick={setCurrentAccountAsHome}>
            {local.home[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Item onclick={showAccountSelection}>
            Change account
        </Dropdown.Item>
        <Dropdown.Separator/>
        <Dropdown.Item onclick={showSettings}>
            {local.settings[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        <Dropdown.Item onclick={minimize}>
            {local.minimize_to_tray[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
        {#if SharedStore.currentAccount !== "home"}
            <Dropdown.Item onclick={logout}>
                <span use:showTooltip={`Logout from ${createSenderAddressFromAccount(SharedStore.currentAccount)}`}>
                    Logout
                </span>
            </Dropdown.Item>
        {/if}
        <Dropdown.Item onclick={quit}>
            {local.quit[DEFAULT_LANGUAGE]}
        </Dropdown.Item>
    </Dropdown.Content>
</Dropdown.Root>
