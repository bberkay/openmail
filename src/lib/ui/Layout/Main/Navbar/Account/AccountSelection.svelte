<script lang="ts" module>
    import { Folder, type Account } from "$lib/types";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/mailbox";
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
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as List from "$lib/ui/Components/List";
    import Icon from "$lib/ui/Components/Icon";
    import * as Pagination from "$lib/ui/Components/Pagination";
    import { getSenderAddressTemplate } from "$lib/templates";
    import Modal from "$lib/ui/Components/Modal";
    import { GravatarService } from "$lib/services/GravatarService";

    const ACCOUNT_COUNT_FOR_EACH_PAGE = 10;

    let simpleSearchInput: HTMLInputElement | undefined = $state();
    let allAccounts: Account[] = $state(
        SharedStore.accounts.slice(0, ACCOUNT_COUNT_FOR_EACH_PAGE),
    );

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
</script>

<Modal class="frameless">
    <Input.Group class="frameless-header">
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
        <Button.Basic type="button" data-modal-close>
            <Icon name="close" />
        </Button.Basic>
    </Input.Group>
    <div class="frameless-body">
        <List.Root>
            <List.Item
                onclick={async () => await setCurrentAccount("home") }
                type={SharedStore.currentAccount === "home" ? "active" : undefined}
            >
                <div class="account-selection-item-container">
                    <div class="account-selection-item">
                        <div class="account-avatar-container home">
                            <Icon name="home" style="width:18px;height:18px;"/>
                        </div>
                        <span>Home</span>
                    </div>
                </div>
            </List.Item>
        </List.Root>
        <List.Root>
            {#each allAccounts as account}
                {@const isSelectedAccount = account === SharedStore.currentAccount}
                <List.Item
                    onclick={async () => await setCurrentAccount(account) }
                    type={isSelectedAccount ? "active" : undefined}
                >
                    <div class="account-selection-item-container">
                        <div class="account-selection-item">
                            <div class="account-avatar-container">
                                {@html GravatarService.renderAvatarData(account.avatar)}
                            </div>
                            <span>
                                {@html getSenderAddressTemplate(
                                    account.email_address,
                                    account.fullname,
                                )}
                            </span>
                        </div>
                        {#if isSelectedAccount}
                            <Icon name="success" style="stroke-width:0px;fill:white;"/>
                        {/if}
                    </div>
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
</Modal>

<style>
    .account-selection-pagination-container {
        margin-top: var(--spacing-md);
    }

    .account-selection-item-container {
        display: flex;
        align-items: center;
        justify-content: space-between;

        & .account-selection-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);

            & .account-avatar-container {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 25px;
                width: 25px;

                &.home {
                    background-color: var(--color-bg-secondary);
                    border-radius: var(--radius-sm);
                    border: 1px solid var(--color-border);
                }
            }
        }
    }
</style>
