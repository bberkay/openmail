<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import {
        getSelectedAccountTemplate,
    } from "$lib/templates";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";
    import Icon from "$lib/ui/Components/Icon";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { show as showConfirm } from "$lib/ui/Components/Confirm";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import type { Account } from "$lib/types";

    interface Props {
        accounts: Account[];
        accountSelection: string[];
        accountSelectionType: "shown" | "all" | false;
        showEditAccount: (account: Account) => void;
        onRemoveAccount?: (email_address: string) => Promise<void>;
        onRemoveAllAccounts?: () => Promise<void>;
    }

    let {
        accounts = $bindable(),
        accountSelection = $bindable(),
        accountSelectionType = $bindable(),
        showEditAccount,
        onRemoveAccount,
        onRemoveAllAccounts
    }: Props = $props();

    const selectShownAccounts = () => {
        accountSelectionType = accountSelectionType === "all"
            ? "shown"
            : accountSelectionType === "shown" ? false : "shown";
        accountSelection = accountSelectionType === "shown"
            ? accounts.map((account) => account.email_address)
            : [];
    };

    const removeAccount = async (e: Event): Promise<void> => {
        const removeAccountWrapper = async (e: Event) => {
            const target = e.target as HTMLButtonElement;
            const email_address = target.getAttribute("data-email-address")!;
            const response = await AccountController.remove(email_address);

            if (!response.success) {
                showMessage({
                    title: local.error_remove_account[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
                return;
            }

            if (onRemoveAccount) await onRemoveAccount(email_address);
        }

        showConfirm({
            title: local.are_you_certain_remove_account[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_remove[DEFAULT_LANGUAGE],
            onConfirm: removeAccountWrapper
        });
    };

    const removeAllAccounts = async (): Promise<void> => {
        const removeAllAccountsWrapper = async (e: Event) => {
            const response = await AccountController.removeAll();

            if (!response.success) {
                showMessage({
                    title: local.error_remove_all_account[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
            }

            if (onRemoveAllAccounts) await onRemoveAllAccounts();
        }

        showConfirm({
            title: local.are_you_certain_remove_all_accounts[DEFAULT_LANGUAGE],
            onConfirmText: local.remove_all[DEFAULT_LANGUAGE],
            onConfirm: removeAllAccountsWrapper
        });
    };
</script>

{#if (SharedStore.accounts && SharedStore.accounts.length > 0) || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)}
{@const failedAccountLength = (SharedStore.failedAccounts || []).length}
<Table.Root class="accounts-table">
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
                <Button.Action
                    class={accountSelection.length > 0
                        ? "btn-inline"
                        : "btn-inline invisible"}
                    disabled={accountSelection.length === 0}
                    onclick={removeAllAccounts}
                >
                    {local.remove_all[DEFAULT_LANGUAGE]}
                </Button.Action>
            </Table.Head>
        </Table.Row>
    </Table.Header>
    <Table.Body>
        {#each accounts as account, index}
            <Table.Row
                class={SharedStore.failedAccounts.includes(account)
                    ? "failed"
                    : ""}
            >
                <Table.Cell class="checkbox-cell">
                    <Input.Basic
                        type="checkbox"
                        bind:group={accountSelection}
                        value={account.email_address}
                    />
                </Table.Cell>
                <Table.Cell class="body-cell">
                    {#if index < failedAccountLength}
                        <Icon name="warning" />
                    {/if}
                    <span>{account.fullname}</span>
                    <small class="muted">&lt;{account.email_address}&gt;</small>
                </Table.Cell>
                <Table.Cell class="action-cell">
                    <div class="action-buttons">
                        <Button.Basic
                            type="button"
                            class="btn-inline"
                            onclick={() => {
                                showEditAccount(account);
                            }}
                        >
                            <Icon name="edit" />
                        </Button.Basic>
                        <Button.Action
                            class="btn-inline"
                            onclick={removeAccount}
                            data-email-address={account.email_address}
                        >
                            <Icon name="trash" />
                        </Button.Action>
                    </div>
                </Table.Cell>
            </Table.Row>
        {/each}
    </Table.Body>
</Table.Root>
{/if}

<style>
    :global {
        .accounts-table {
            & .tr:has(.checkbox-cell input[type="checkbox"]:checked) {
                background-color: var(--color-hover)!important;
            }

            & .checkbox-cell {
                width: var(--font-size-2xl);
                padding-left: var(--spacing-sm);
                padding-top: var(--spacing-md);
            }

            & .body-cell {
                padding-left: var(--spacing-xs);
                padding-top: var(--spacing-md);
                text-align: left;

                & span {
                    margin-right: var(--spacing-2xs);

                    &:not(:first-child) {
                        margin-left: var(--spacing-2xs);
                    }
                }
            }

            & .action-cell {
                padding-right: var(--spacing-sm);
                width: calc(2 * var(--font-size-2xl));

                & .action-buttons {
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    gap: var(--spacing-sm);

                    & svg {
                        width: var(--font-size-md);
                        height: var(--font-size-md);
                    }
                }
            }
        }
    }
</style>
