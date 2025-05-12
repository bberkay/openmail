<script lang="ts">
    import type { Account } from "$lib/types";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import { onMount } from "svelte";

    interface Props {
        allAccounts: Account[];
        accounts: Account[];
        accountSelection: string[];
        accountSelectionType: "shown" | "all" | false;
    }

    let {
        allAccounts = $bindable(),
        accounts = $bindable(),
        accountSelection = $bindable(),
        accountSelectionType = $bindable()
    }: Props = $props();

    let selectShownCheckbox: HTMLInputElement;

    onMount(() => selectShownCheckbox = document.getElementById("select-shown-checkbox") as HTMLInputElement);

    const selectAllAccounts = (event: Event) => {
        accountSelectionType = accountSelectionType === "shown" ? "all" : false;
        const selectAllCheckbox = event.target as HTMLButtonElement;
        selectAllCheckbox.innerText = accountSelectionType === "all" ? "Clear Selection" : "Select All";
        accountSelection = accountSelectionType === "all"
            ? allAccounts.map((account) => account.email_address)
            : [];
        selectShownCheckbox.checked = !!accountSelectionType;
    };

    const searchAccounts = (e: Event) => {
        const target = e.target as HTMLInputElement;
        accounts = allAccounts.filter(
            (account) =>
                account.email_address
                    .toLowerCase()
                    .includes(target.value.toLowerCase()) ||
                account.fullname
                    ?.toLowerCase()
                    .includes(target.value.toLowerCase()),
        );
    };

    $effect(() => {
        if (accountSelectionType === "all") {
            selectShownCheckbox.checked = accountSelection.length !== allAccounts.length;
        }
        else if (accountSelectionType === "shown"){
            selectShownCheckbox.checked = accounts.every(acc => accountSelection.includes(acc.email_address));
        }
    });
</script>

<div class="accounts-info">
    {#if accountSelectionType}
        <Button.Basic
            type="button"
            class="btn-outline"
            onclick={selectAllAccounts}
        >
            Select All
        </Button.Basic>
    {:else}
        <Input.Expandable
            type="text"
            placeholder="Search accounts..."
            onkeyup={searchAccounts}
            onClose={() => {
                accounts = allAccounts;
            }}
        />
    {/if}
</div>

<style>
    :global {
        .accounts-info {
            display: flex;
            justify-content: space-between;
            flex-direction: row;
            align-items: end;
            margin-bottom: var(--spacing-xs);
        }
    }
</style>
