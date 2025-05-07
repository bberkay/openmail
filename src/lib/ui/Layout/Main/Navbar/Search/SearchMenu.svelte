<script lang="ts">
    import { fade } from "svelte/transition";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        Folder,
        type SearchCriteria,
        type Account as TAccount,
    } from "$lib/types";
    import {
        debounce,
        isObjEmpty,
        createSenderAddress,
        createSenderAddressFromAccount,
    } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import {
        DEFAULT_LANGUAGE,
        GENERAL_FADE_DURATION_MS,
        REALTIME_SEARCH_DELAY_MS,
    } from "$lib/constants";
    import { local } from "$lib/locales";
    import { getSearchForAccountTemplate } from "$lib/templates";
    import Cc from "./SearchMenu/Cc.svelte";
    import Subject from "./SearchMenu/Subject.svelte";
    import Include from "./SearchMenu/Include.svelte";
    import Exclude from "./SearchMenu/Exclude.svelte";
    import Folders from "./SearchMenu/Folders.svelte";
    import Senders from "./SearchMenu/Senders.svelte";
    import Receivers from "./SearchMenu/Receivers.svelte";
    import Flags from "./SearchMenu/Flags.svelte";
    import Date from "./SearchMenu/Date.svelte";
    import Size from "./SearchMenu/Size.svelte";
    import Attachments from "./SearchMenu/Attachments.svelte";
    import Account from "./SearchMenu/Account.svelte";
    import Action from "./SearchMenu/Action.svelte";

    interface Props {
        isSimpleSearchHidden: boolean;
    }

    let { isSimpleSearchHidden = $bindable() }: Props = $props();

    let isExtraOptionsHidden = $state(true);

    let searchCriteria: SearchCriteria = $state({});
    let searchingAccounts: "home" | TAccount[] = $state(
        SharedStore.currentAccount == "home"
            ? "home"
            : [SharedStore.currentAccount],
    );
    let searchingFolder: string | Folder = $state(Folder.All);
    let simpleSearchInput: HTMLInputElement | undefined = $state(undefined);

    const search = async (
        accounts: TAccount[],
        searchCriteriaOrKeywords: SearchCriteria | string,
    ): Promise<void> => {
        if (accounts.length > 1)
            searchingFolder = Folder.All;

        const results = await Promise.allSettled(
            accounts.map(async (account) => {
                const response = await MailboxController.getMailbox(
                    account,
                    searchingFolder,
                    searchCriteriaOrKeywords,
                );
                if (!response.success) {
                    throw new Error(response.message);
                }
            }),
        );

        const failed = results.filter((r) => r.status === "rejected");

        if (failed.length > 0) {
            showMessage({
                title: local.error_search_emails[DEFAULT_LANGUAGE],
            });
            failed.forEach((f) => console.error(f.reason));
        }
    };

    const debouncedSearch = debounce(async (e: KeyboardEvent) => {
        await simpleSearch();
    }, REALTIME_SEARCH_DELAY_MS);

    const simpleSearch = async () => {
        if (simpleSearchInput!.value.length >= 3) {
            await search(
                SharedStore.currentAccount === "home"
                    ? SharedStore.accounts
                    : [SharedStore.currentAccount],
                simpleSearchInput!.value
            );
        }
    };

    const advancedSearch = async () => {
        if (!isExtraOptionsHidden && !isObjEmpty(searchCriteria)) {
            await search(
                searchingAccounts === "home"
                    ? SharedStore.accounts
                    : searchingAccounts,
                searchCriteria
            );
        }
    };

    const toggleSimpleSearch = () => {
        isSimpleSearchHidden = !isSimpleSearchHidden;
    };

    const toggleExtraOptions = () => {
        isExtraOptionsHidden = !isExtraOptionsHidden;
    };
</script>

{#if !isSimpleSearchHidden}
    <!-- to trigger modal overlay -->
    <div class="modal" style="display:none"></div>
    <div
        class="search-menu modal-like"
        transition:fade={{ duration: GENERAL_FADE_DURATION_MS }}
    >
        <Input.Group class="modal-like-header">
            <Button.Action type="button" onclick={simpleSearch}>
                <Icon name="search" />
            </Button.Action>
            <Input.Basic
                bind:element={simpleSearchInput}
                type="text"
                id="simple-search"
                placeholder={getSearchForAccountTemplate(
                    (SharedStore.currentAccount !== "home"
                        ? [SharedStore.currentAccount]
                        : SharedStore.accounts
                    )
                        .map((acc) => createSenderAddressFromAccount(acc))
                        .join(","),
                )}
                onkeyup={debouncedSearch}
                onblur={debouncedSearch}
            />
            <Button.Basic type="button" onclick={toggleSimpleSearch}>
                <Icon name="close" />
            </Button.Basic>
            <Button.Basic type="button" onclick={toggleExtraOptions}>
                <Icon name="funnel" />
            </Button.Basic>
        </Input.Group>
        <div class="modal-like-body {isExtraOptionsHidden ? 'hidden' : ''}">
            <Account bind:searchingAccounts />
            <Folders bind:searchingAccounts bind:searchingFolder />
            <Senders bind:searchCriteria />
            <Receivers bind:searchCriteria />
            <Cc bind:searchCriteria />
            <Subject bind:searchCriteria />
            <Date bind:searchCriteria />
            <Include bind:searchCriteria />
            <Exclude bind:searchCriteria />
            <Flags bind:searchCriteria />
            <Size bind:searchCriteria />
            <Attachments bind:searchCriteria />
            <Action bind:searchCriteria onSearch={advancedSearch} />
        </div>
    </div>
{/if}

<style>
    :global {
        .search-menu {
            & .modal-like-body {
                & .searching-account {
                    width: 100%;
                    margin-top: var(--spacing-2xs);
                }

                & .search-button-group {
                    justify-content: end;
                    gap: var(--spacing-md);
                }
            }
        }
    }
</style>
