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
    import { createSenderAddressFromAccount } from "$lib/utils";

    interface Props {
        searchingAccounts: "home" | Account[];
    }

    let { searchingAccounts = $bindable() }: Props = $props();

    let isAccountSelectionHidden = $state(true);

    const selectSearchingAccount = (selectedAccounts: "home" | Account[]) => {
        searchingAccounts = selectedAccounts;
    };

    const showAccountSelection = () => {
        isAccountSelectionHidden = false;
    };
</script>

<FormGroup>
    <Label for="searching-account">
        {local.searching_account[DEFAULT_LANGUAGE]}
    </Label>
    <Button.Basic onclick={showAccountSelection}>
        {getSearchForAccountTemplate(
            (searchingAccounts === "home"
                ? SharedStore.accounts
                : searchingAccounts
            )
                .map((acc) => createSenderAddressFromAccount(acc))
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
                    content={createSenderAddressFromAccount(account)}
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

<AccountSelection
    bind:isAccountSelectionHidden
    allowMultipleSelection={true}
    actionOnSelect={selectSearchingAccount}
    initialSelectedAccounts={searchingAccounts}
/>
