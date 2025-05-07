<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import type { Account } from "$lib/types";
    import Label from "$lib/ui/Components/Label";
    import * as Button from "$lib/ui/Components/Button";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import {
        getSearchForAccountTemplate,
    } from "$lib/templates";
    import AccountSelection from "$lib/ui/Layout/Main/Portable/AccountSelection.svelte";
    import { createSenderAddressFromAccount, escapeHTML } from "$lib/utils";
    import { show as showModal } from "$lib/ui/Components/Modal";

    interface Props {
        searchingAccounts: "home" | Account[];
    }

    let {
        searchingAccounts = $bindable()
    }: Props = $props();

    const selectSearchingAccount = (selectedAccounts: "home" | Account[]) => {
        searchingAccounts = selectedAccounts;
    };

    const showAccountSelection = () => {
        showModal(AccountSelection, {
            allowMultipleSelection: true,
            actionOnSelect: selectSearchingAccount,
            initialSelectedAccounts: searchingAccounts
        });
    };
</script>

<FormGroup>
    <Label>
        {local.searching_account[DEFAULT_LANGUAGE]}
    </Label>
    <Button.Basic
        class="btn-outline account-selection-toggle"
        onclick={showAccountSelection}
    >
        {getSearchForAccountTemplate(
            (searchingAccounts === "home"
                ? SharedStore.accounts
                : searchingAccounts
            )
                .map((acc) => escapeHTML(createSenderAddressFromAccount(acc)))
                .join(","),
        )}
    </Button.Basic>
    <div class="tags">
        {#if searchingAccounts}
            {@const searchingAccountList =
                searchingAccounts === "home"
                    ? SharedStore.accounts
                    : searchingAccounts}
            {#each searchingAccountList as account}
                <Badge
                    content={escapeHTML(createSenderAddressFromAccount(account))}
                    righticon="close"
                    onclick={() => {
                        if (searchingAccounts === "home") return;
                        searchingAccounts = searchingAccounts.filter(
                            (acc) =>
                                account.email_address !== acc.email_address,
                        );
                    }}
                />
            {/each}
        {/if}
    </div>
</FormGroup>

<style>
    :global {
        .search-menu {
            & .account-selection-toggle {
                text-align: left;
                margin-top: var(--spacing-2xs);
                font-size: var(--font-size-xs);
            }
        }
    }
</style>
