<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { getSelectedAccountTemplate } from "$lib/templates";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import Icon from "$lib/ui/Components/Icon";
    import { DEFAULT_LANGUAGE, DEFAULT_PREFERENCES } from "$lib/constants";
    import { local } from "$lib/locales";
    import type { Account, NotificationStatus } from "$lib/types";
    import { onMount } from "svelte";
    import { NotificationHandler } from "$lib/services/NotificationHandler";

    interface Props {
        shownAccounts: Account[];
        accountSelection: string[];
        accountSelectionType: "shown" | "all" | "parts";
    }

    let {
        shownAccounts = $bindable(),
        accountSelection = $bindable(),
        accountSelectionType = $bindable(),
    }: Props = $props();

    let newNotificationStatus: NotificationStatus = $state(
        SharedStore.preferences.notificationStatus,
    );

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown-checkbox",
        ) as HTMLInputElement;
        document.removeEventListener(
            "preferencesSaved",
            saveNotificationChange,
        );
        document.addEventListener("preferencesSaved", saveNotificationChange);
        document.removeEventListener(
            "preferencesResetToDefault",
            resetNotificationChange,
        );
        document.addEventListener(
            "preferencesResetToDefault",
            resetNotificationChange,
        );
    });

    function saveNotificationChange() {
        if (newNotificationStatus instanceof Boolean) {
            SharedStore.preferences.notificationStatus = newNotificationStatus;
            if (newNotificationStatus === false) {
                Object.values(SharedStore.notificationChannels).forEach(ch => ch.terminate());
                SharedStore.notificationChannels = {};
            } else {
                SharedStore.accounts.forEach((acc) => {
                    if (!Object.hasOwn(SharedStore.notificationChannels, acc.email_address)) {
                        SharedStore.notificationChannels[acc.email_address] = new NotificationHandler(acc);
                    } else {
                        SharedStore.notificationChannels[acc.email_address].reinitialize();
                    }
                });
            }
        } else {
            Object.entries(newNotificationStatus).forEach(([email_address, status]) => {
                const isNotificationEnabled = (newNotificationStatus as {[email_address]: boolean})[email_address];
                (SharedStore.preferences.notificationStatus as Record<string, boolean>)[email_address] = status;
                if (Object.hasOwn(SharedStore.notificationChannels, email_address)) {
                    if (isNotificationEnabled) {
                        SharedStore.notificationChannels[email_address].reinitialize();
                    } else {
                        SharedStore.notificationChannels[email_address].terminate();
                        delete SharedStore.notificationChannels[email_address];
                    }
                } else {
                    if (isNotificationEnabled) {
                        const acc = SharedStore.accounts.find(acc => acc.email_address === email_address)!;
                        SharedStore.notificationChannels[email_address] = new NotificationHandler(acc);
                    }
                }
            });
        }
    }

    function resetNotificationChange() {
        newNotificationStatus = DEFAULT_PREFERENCES.notificationStatus;
        saveNotificationChange();
    }

    function isNotificationAllowed(account: Account): boolean {
        if (!(SharedStore.preferences.notificationStatus instanceof Object))
            return SharedStore.preferences.notificationStatus;

        return Object.hasOwn(
            SharedStore.preferences.notificationStatus,
            account.email_address,
        );
    }

    const selectShownAccounts = () => {
        accountSelectionType =
            accountSelectionType === "parts" ? "shown" : "parts";

        accountSelection =
            accountSelectionType === "shown"
                ? shownAccounts.map((account) => account.email_address)
                : [];
    };

    const deselectShownAccounts = () => {
        accountSelectionType = "parts";
        selectShownCheckbox.checked = false;
    };

    const toggleNotification = async (account: Account, toggle: boolean) => {
        if (!(newNotificationStatus instanceof Object))
            newNotificationStatus = {};

        newNotificationStatus[account.email_address] = toggle;
    };

    const toggleNotifications = async (checked: boolean) => {
        newNotificationStatus = checked;
    };
</script>

{#if SharedStore.accounts && SharedStore.accounts.length > 0}
    <Table.Root
        class={`account-table ${shownAccounts.length === 0 ? "disabled" : ""}`}
    >
        <Table.Header>
            <Table.Row>
                <Table.Head class="checkbox-cell">
                    <Input.Basic
                        id="select-shown-checkbox"
                        type="checkbox"
                        onclick={selectShownAccounts}
                    />
                </Table.Head>
                <Table.Head class="body-cell">
                    {accountSelection.length > 0
                        ? getSelectedAccountTemplate(
                              accountSelection.length.toString(),
                          )
                        : local.account[DEFAULT_LANGUAGE]}
                </Table.Head>
                <Table.Head>
                    <Input.ToggleSwitch
                        class={accountSelection.length === 0 ? "invisible" : ""}
                        disabled={accountSelection.length === 0}
                        onchange={toggleNotifications}
                        defaultChecked={!!SharedStore.preferences
                            .notificationStatus}
                    />
                </Table.Head>
            </Table.Row>
        </Table.Header>
        <Table.Body>
            {#each shownAccounts as account}
                <Table.Row>
                    <Table.Cell class="checkbox-cell">
                        <Input.Basic
                            type="checkbox"
                            bind:group={accountSelection}
                            onclick={deselectShownAccounts}
                            value={account.email_address}
                        />
                    </Table.Cell>
                    <Table.Cell class="body-cell">
                        <span>{account.fullname}</span>
                        <small class="muted">
                            &lt;{account.email_address}&gt;
                        </small>
                    </Table.Cell>
                    <Table.Cell class="action-cell">
                        <div class="action-buttons">
                            <Input.ToggleSwitch
                                onchange={(checked) =>
                                    toggleNotification(account, checked)}
                                defaultChecked={isNotificationAllowed(account)}
                            />
                        </div>
                    </Table.Cell>
                </Table.Row>
            {:else}
                <Table.Row>
                    <Table.Cell colspan="3" class="full">
                        <div class="no-match-results">
                            <Icon name="warning" />
                            <span>No results found</span>
                        </div>
                    </Table.Cell>
                </Table.Row>
            {/each}
        </Table.Body>
    </Table.Root>
{/if}
