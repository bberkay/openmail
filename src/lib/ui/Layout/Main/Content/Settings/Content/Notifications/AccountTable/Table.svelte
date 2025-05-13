<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { getSelectedAccountTemplate } from "$lib/templates";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import Icon from "$lib/ui/Components/Icon";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import type { Account } from "$lib/types";
    import { simpleDeepCopy } from "$lib/utils";
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

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById("select-shown-checkbox") as HTMLInputElement;
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

    const toggleNotification = async (account: Account, toggle?: boolean) => {
        if (Object.hasOwn(SharedStore.notificationChannels, account.email_address)) {
            if (toggle === true) return;
            SharedStore.notificationChannels[account.email_address].terminate();
            delete SharedStore.notificationChannels[account.email_address];
        } else {
            if (toggle === false) return;
            SharedStore.notificationChannels[account.email_address] = new NotificationHandler(account);
        }
    }

    const toggleNotifications = async () => {
        // TODO: Fix here, add toggle parameter, check toggle notifications toggle switch.
        SharedStore.accounts.map(acc => {
            if(accountSelection.includes(acc.email_address)) {
                toggleNotification(acc);
            }
        })
    }
</script>

{#if SharedStore.accounts && SharedStore.accounts.length > 0}
    <Table.Root class={`account-table ${shownAccounts.length === 0 ? "disabled" : ""}`}>
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
                        onclick={toggleNotifications}
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
                                onclick={() => toggleNotification(account)}
                            />
                        </div>
                    </Table.Cell>
                </Table.Row>
            {:else}
                <Table.Row>
                    <Table.Cell colspan="3" class="full">
                        <div class="no-match-results">
                            <Icon name="warning"/>
                            <span>No results found</span>
                        </div>
                    </Table.Cell>
                </Table.Row>
            {/each}
        </Table.Body>
    </Table.Root>
{/if}
