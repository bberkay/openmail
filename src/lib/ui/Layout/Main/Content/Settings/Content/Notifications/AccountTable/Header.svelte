<script lang="ts">
    import type { Account } from "$lib/types";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import { onMount } from "svelte";

    interface Props {
        allAccounts: Account[];
        shownAccounts: Account[];
        accountSelection: string[];
        accountSelectionType: "shown" | "all" | "parts";
    }

    let {
        allAccounts = $bindable(),
        shownAccounts = $bindable(),
        accountSelection = $bindable(),
        accountSelectionType = $bindable(),
    }: Props = $props();

    let selectShownCheckbox: HTMLInputElement;
    onMount(() => {
        selectShownCheckbox = document.getElementById("select-shown-checkbox") as HTMLInputElement;
    });

    const selectAllAccounts = () => {
        accountSelectionType = "all";
        accountSelection = allAccounts.map((account) => account.email_address);
    };

    const clearSelection = () => {
        accountSelectionType = "parts";
        accountSelection = [];
        selectShownCheckbox.checked = false;
    };

    const searchAccounts = (e: Event) => {
        const target = e.target as HTMLInputElement;
        shownAccounts = allAccounts.filter((account) => {
            const isInEmailAddress = account.email_address
                .toLowerCase()
                .includes(target.value.toLowerCase());

            const isInFullname = account.fullname
                ?.toLowerCase()
                .includes(target.value.toLowerCase());

            return isInEmailAddress || isInFullname;
        });
    };

    const showAllAccounts = () => {
        shownAccounts = allAccounts;
    };
</script>

<div class="accounts-info">
    {#if accountSelectionType === "shown"}
        <Button.Basic
            type="button"
            class="btn-outline"
            onclick={selectAllAccounts}
        >
            Select All
        </Button.Basic>
    {:else if accountSelectionType === "all"}
        <Button.Basic
            type="button"
            class="btn-outline"
            onclick={clearSelection}
        >
            Clear Selection
        </Button.Basic>
    {:else}
        <Input.Expandable
            type="text"
            placeholder="Search accounts..."
            onkeyup={searchAccounts}
            onClose={showAllAccounts}
            collapsedWidth={30}
            expandedWidth={300}
        />
    {/if}
</div>
