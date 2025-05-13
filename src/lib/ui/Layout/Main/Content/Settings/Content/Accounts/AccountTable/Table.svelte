<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { AccountController } from "$lib/controllers/AccountController";
    import { getSelectedAccountTemplate } from "$lib/templates";
    import * as Button from "$lib/ui/Components/Button";
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
    import { show as showModal } from "$lib/ui/Components/Modal";
    import EditAccountForm from "../EditAccountForm.svelte";
    import type { PostResponse, PostRoutes } from "$lib/services/ApiService";

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

    const resetAccountSelection = () => {
        accountSelectionType = "parts";
        accountSelection = [];
        selectShownCheckbox.checked = false;
    };

    const removeAccount = async (account: Account): Promise<void> => {
        resetAccountSelection();

        const removeAccountWrapper = async () => {
            const response = await AccountController.remove(
                account.email_address,
            );

            if (!response.success) {
                showMessage({
                    title: local.error_remove_account[DEFAULT_LANGUAGE],
                });
                console.error(response.message);
                return;
            }
        };

        showConfirm({
            title: local.are_you_certain_remove_account[DEFAULT_LANGUAGE],
            onConfirmText: local.yes_remove[DEFAULT_LANGUAGE],
            onConfirm: removeAccountWrapper,
        });
    };

    const removeSelectedAccounts = async (): Promise<void> => {
        const removeSelectedAccountsWrapper = async () => {
            const failed: PostResponse<PostRoutes>[] = [];
            accountSelection.forEach(async (email_address) => {
                const response = await AccountController.remove(email_address);
                if (!response.success) failed.push(response);
            });

            resetAccountSelection();

            if (failed.length > 0) {
                showMessage({
                    title: local.error_remove_all_account[DEFAULT_LANGUAGE],
                });
                failed.forEach((f) => console.error(f.message));
                return;
            }
        };

        showConfirm({
            title: local.are_you_certain_remove_all_accounts[DEFAULT_LANGUAGE],
            onConfirmText: local.remove_all[DEFAULT_LANGUAGE],
            onConfirm: removeSelectedAccountsWrapper,
        });
    };

    const showEditAccount = async (account: Account) => {
        resetAccountSelection();
        showModal(EditAccountForm, { account });
    };
</script>

{#if (SharedStore.accounts && SharedStore.accounts.length > 0) || (SharedStore.failedAccounts && SharedStore.failedAccounts.length > 0)}
    {@const failedAccountLength = (SharedStore.failedAccounts || []).length}
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
                    <Button.Action
                        class={`btn-inline ${accountSelection.length === 0 ? "invisible" : ""}`}
                        disabled={accountSelection.length === 0}
                        onclick={removeSelectedAccounts}
                    >
                        {local.remove[DEFAULT_LANGUAGE]}
                    </Button.Action>
                </Table.Head>
            </Table.Row>
        </Table.Header>
        <Table.Body>
            {#each shownAccounts as account, index}
                <Table.Row
                    class={SharedStore.failedAccounts.includes(account)
                        ? "failed"
                        : ""}
                >
                    <Table.Cell class="checkbox-cell">
                        <Input.Basic
                            type="checkbox"
                            bind:group={accountSelection}
                            onclick={deselectShownAccounts}
                            value={account.email_address}
                        />
                    </Table.Cell>
                    <Table.Cell class="body-cell">
                        {#if index < failedAccountLength}
                            <Icon name="warning" />
                        {/if}
                        <span>{account.fullname}</span>
                        <small class="muted">
                            &lt;{account.email_address}&gt;
                        </small>
                    </Table.Cell>
                    <Table.Cell class="action-cell">
                        <div class="action-buttons">
                            <Button.Basic
                                type="button"
                                class="btn-inline"
                                onclick={() => showEditAccount(account)}
                            >
                                <Icon name="edit" />
                            </Button.Basic>
                            <Button.Action
                                class="btn-inline"
                                onclick={() => removeAccount(account)}
                            >
                                <Icon name="trash" />
                            </Button.Action>
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

<style>
    :global {
        .account-table {
            & .action-cell {
                & .action-buttons {
                    gap: var(--spacing-lg);

                    & svg {
                        width: var(--font-size-md);
                        height: var(--font-size-md);
                    }
                }
            }
        }
    }
</style>
