<script lang="ts" module>
    import { Folder, type Account } from "$lib/types";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { isStandardFolder } from "$lib/utils";
    import Mailbox from "$lib/ui/Layout/Main/Content/Mailbox.svelte";
    import { showThis as showContent } from "$lib/ui/Layout/Main/Content.svelte";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    export const setCurrentAccount = async (
        homeOrAccount: "home" | Account,
    ): Promise<void> => {
        const newAccount =
            homeOrAccount === "home"
                ? "home"
                : SharedStore.accounts.find(
                      (account: Account) =>
                          account.email_address === homeOrAccount.email_address,
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
</script>

<script lang="ts">
    import { fade } from "svelte/transition";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as List from "$lib/ui/Components/List";
    import Icon from "$lib/ui/Components/Icon";
    import { GENERAL_FADE_DURATION_MS } from "$lib/constants";
    import * as Pagination from "$lib/ui/Components/Pagination";
    import { getSenderAddressTemplate } from "$lib/templates";

    const ACCOUNT_COUNT_FOR_EACH_PAGE = 10;

    type ActionOnSelect<T extends boolean> = T extends true
        ? (selectedAccounts: "home" | Account[]) => void | Promise<void>
        : (selectedAccounts: "home" | Account) => void | Promise<void>;

    interface Props<T extends boolean> {
        isAccountSelectionHidden: boolean;
        allowMultipleSelection: T;
        actionOnSelect: ActionOnSelect<T>;
        initialSelectedAccounts?: T extends true
            ? "home" | Account[]
            : "home" | Account;
    }

    let {
        isAccountSelectionHidden = $bindable(),
        allowMultipleSelection,
        actionOnSelect,
        initialSelectedAccounts,
    }: Props<boolean> = $props();

    let simpleSearchInput: HTMLInputElement | undefined = $state();
    let allAccounts: Account[] = $state(
        SharedStore.accounts.slice(0, ACCOUNT_COUNT_FOR_EACH_PAGE),
    );
    let selectedAccounts = $state(
        initialSelectedAccounts || (allowMultipleSelection ? [] : undefined),
    );

    const selectAccount = async (account: "home" | Account) => {
        if (!allowMultipleSelection || account === "home") {
            selectedAccounts = account;
            await (actionOnSelect as ActionOnSelect<false>)(selectedAccounts);
            return;
        }

        const typedSelectedAccounts = selectedAccounts as Account[];
        const typedActionOnSelect = actionOnSelect as ActionOnSelect<true>;

        if (selectedAccounts === "home" || typedSelectedAccounts.includes(account)) {
            selectedAccounts = typedSelectedAccounts.filter(
                (acc) => acc !== account,
            );
            await typedActionOnSelect(selectedAccounts);
            return;
        }

        if (!typedSelectedAccounts.includes(account)) {
            typedSelectedAccounts.push(account);
            await typedActionOnSelect(typedSelectedAccounts);
            return;
        }
    };

    const search = () => {
        if (!simpleSearchInput || simpleSearchInput.value.length < 3) return;

        allAccounts = SharedStore.accounts.filter((acc) => {
            acc.email_address.includes(simpleSearchInput!.value) ||
                (acc.fullname &&
                    acc.fullname.includes(simpleSearchInput!.value));
        });
    };

    const updateAccountPage = (newOffset: number) => {
        allAccounts = SharedStore.accounts.slice(
            newOffset - ACCOUNT_COUNT_FOR_EACH_PAGE,
            newOffset,
        );
    };

    const toggleAccountSelection = () => {
        isAccountSelectionHidden = !isAccountSelectionHidden;
    };
</script>

{#if !isAccountSelectionHidden}
    <!-- to trigger modal overlay -->
    <div class="modal" style="display:none"></div>
    <div
        class="account-search-menu modal-like"
        transition:fade={{ duration: GENERAL_FADE_DURATION_MS }}
    >
        <Input.Group class="modal-like-header">
            <Button.Action type="button" onclick={search}>
                <Icon name="search" />
            </Button.Action>
            <Input.Basic
                bind:element={simpleSearchInput}
                type="text"
                id="simple-search"
                placeholder="Search an account by email address or fullname..."
                onkeyup={search}
                onblur={search}
            />
            <Button.Basic type="button" onclick={toggleAccountSelection}>
                <Icon name="close" />
            </Button.Basic>
        </Input.Group>
        <div class="modal-like-body">
            <List.Root>
                <List.Item
                    onclick={async () => {
                        await selectAccount("home");
                    }}
                    type={selectedAccounts === "home" ? "active" : undefined}
                >
                    Home
                </List.Item>
            </List.Root>
            <hr />
            <List.Root>
                {#each allAccounts as account}
                    {@const isSelectedAccount =
                        selectedAccounts === "home" ||
                        (!allowMultipleSelection &&
                            selectedAccounts === account) ||
                        (allowMultipleSelection &&
                            (selectedAccounts as Account[]).includes(account))}
                    <List.Item
                        onclick={async () => {
                            await selectAccount(account);
                        }}
                        type={isSelectedAccount ? "active" : undefined}
                    >
                        {#if isSelectedAccount}
                            <Icon name="success" />
                        {/if}
                        {@html getSenderAddressTemplate(
                            account.email_address,
                            account.fullname,
                        )}
                    </List.Item>
                {/each}
            </List.Root>
            {#if allAccounts.length > ACCOUNT_COUNT_FOR_EACH_PAGE}
                <div class="account-selection-pagination-container">
                    <Pagination.Pages
                        total={SharedStore.accounts.length}
                        offsetStep={ACCOUNT_COUNT_FOR_EACH_PAGE}
                        onChange={updateAccountPage}
                    />
                </div>
            {/if}
        </div>
    </div>
{/if}

<style>
    :global {
        .account-selection-pagination-container {
            margin-top: var(--spacing-md);
        }
    }
</style>
