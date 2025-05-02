<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Label from "$lib/ui/Components/Label";
    import * as Select from "$lib/ui/Components/Select";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { getSenderAddressTemplate } from "$lib/templates";

    interface Props {
        searchingAccount: typeof SharedStore.currentAccount;
    }

    let { searchingAccount = $bindable() }: Props = $props();

    const selectSearchingAccount = (selectedAccount: string) => {
        searchingAccount =
            selectedAccount === "home"
                ? selectedAccount
                : SharedStore.accounts.find(
                      (acc) => acc.email_address === selectedAccount,
                  )!;
    };
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
    >
        <Select.Option value="home" content={local.home[DEFAULT_LANGUAGE]} />
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
</FormGroup>
