<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { getSelectedAccountTemplate } from "$lib/templates";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import Icon from "$lib/ui/Components/Icon";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import type { Account, NotificationStatus } from "$lib/types";
    import { onMount } from "svelte";
    import { GravatarService } from "$lib/services/GravatarService";
    import { PreferenceManager } from "$lib/managers/PreferenceManager";
    import { PreferencesStore } from "$lib/stores/PreferencesStore";

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

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById(
            "select-shown-checkbox",
        ) as HTMLInputElement;
    });

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

    const changeNotificationStatus = (newNotificationStatus: NotificationStatus) => {
        PreferenceManager.changeNotificationStatus(newNotificationStatus);
    }

    const toggleNotification = async (account: Account, toggle: boolean) => {
        PreferenceManager.changeNotificationStatus({[account.email_address]: toggle});
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
                        onchange={changeNotificationStatus}
                        checked={!!PreferencesStore.notificationStatus}
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
                        <span>
                            {@html GravatarService.renderAvatarData(account.avatar)}
                        </span>
                        <span>
                            {account.fullname}
                            <br>
                            <small class="muted">
                                &lt;{account.email_address}&gt;
                            </small>
                        </span>
                    </Table.Cell>
                    <Table.Cell class="action-cell">
                        <div class="action-buttons">
                            <Input.ToggleSwitch
                                onchange={(checked) => {
                                    toggleNotification(account, checked)
                                }}
                                checked={PreferenceManager.checkNotificationStatus(
                                    account.email_address
                                )}
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
