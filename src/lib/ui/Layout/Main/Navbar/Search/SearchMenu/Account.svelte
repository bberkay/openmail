<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import Label from "$lib/ui/Components/Label";
    import * as Button from "$lib/ui/Components/Button";
    import * as Select from "$lib/ui/Components/Select";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { getSenderAddressTemplate } from "$lib/templates";
    import { createSenderAddressFromAccount, escapeHTML } from "$lib/utils";

    interface Props {
        searchingAccounts: "home" | Account[];
    }

    let { searchingAccounts = $bindable() }: Props = $props();

    const selectSearchingAccount = (selectedEmailAddrOrHome: string) => {
        if (selectedEmailAddrOrHome === "home") {
            searchingAccounts = selectedEmailAddrOrHome;
            return;
        }

        const selectedAccount = SharedStore.accounts.find(
            acc => acc.email_address === selectedEmailAddrOrHome
        );
        if (!selectedAccount) return;

        if (searchingAccounts === "home") {
            searchingAccounts = [selectedAccount];
            return;
        }

        if (!searchingAccounts.includes(selectedAccount)) {
            searchingAccounts.push(selectedAccount);
        }
    };

    const removeSearchingAccount = (removingAccount: Account) => {
        if (searchingAccounts === "home") {
            searchingAccounts = SharedStore.accounts.filter(
                acc => acc !== removingAccount
            );
        } else {
            searchingAccounts = searchingAccounts.filter(
                (acc) => acc !== removingAccount,
            );
        }
    }
</script>

<FormGroup>
    <Label for="searching-account">
        {local.searching_account[DEFAULT_LANGUAGE]}
    </Label>
    <Select.Root
        id="searching-account"
        class="searching-account"
        value={SharedStore.currentAccount === "home"
            ? "home"
            : SharedStore.currentAccount.email_address}
        onchange={selectSearchingAccount}
        enableSearch={true}
    >
        <Select.Option value="home" pinned={true} content={local.home[DEFAULT_LANGUAGE]} />
        <Select.Separator />
        {#each SharedStore.accounts as account}
            <Select.Option
                value={account.email_address}
                content={getSenderAddressTemplate(
                    account.email_address,
                    account.fullname,
                )}
            />
        {/each}
    </Select.Root>
    <div class="tags">
        {#if searchingAccounts}
            {@const searchingAccountList =
                searchingAccounts === "home"
                    ? SharedStore.accounts
                    : searchingAccounts}
            {#each searchingAccountList as account}
                <Badge
                    content={
                        getSenderAddressTemplate(account.email_address, account.fullname)
                    }
                    righticon="close"
                    onclick={() => removeSearchingAccount(account)}
                />
            {/each}
        {/if}
    </div>
</FormGroup>

<style>
    :global {
        .search-menu {
            & .searching-account {
                width: 100%;

                & .options-container {
                    max-height: 150px;
                }
            }
        }
    }
</style>
