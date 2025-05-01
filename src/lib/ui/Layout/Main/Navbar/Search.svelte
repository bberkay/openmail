<script lang="ts">
    import { fade } from "svelte/transition";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import {
        Folder,
        Mark,
        type SearchCriteria,
        type Account,
    } from "$lib/types";
    import {
        debounce,
        addEmailToAddressList,
        adjustSizes,
        convertToIMAPDate,
        concatValueAndUnit,
        convertSizeToBytes,
        isObjEmpty,
        createSenderAddress,
    } from "$lib/utils";
    import { Size } from "$lib/types";
    import * as Select from "$lib/ui/Components/Select";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import Icon from "$lib/ui/Components/Icon";
    import Label from "$lib/ui/Components/Label";
    import Badge from "$lib/ui/Components/Badge";
    import { FormGroup } from "$lib/ui/Components/Form";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import { getSearchForAccountTemplate, getSenderAddressTemplate } from "$lib/templates";

    const REALTIME_SEARCH_DELAY_MS = 300;

    let isSimpleSearchHidden = $state(true);
    let isExtraOptionsHidden = $state(true);

    let searchingFolder: string | Folder = $state(Folder.All);
    let searchCriteria: SearchCriteria = $state({});

    let searchMenu: HTMLElement | null = $state(null);
    let extraOptionsWrapper: HTMLElement | null = $state(null);
    let simpleSearchInput: HTMLInputElement;

    let selectedSince: Date | undefined = $state();
    let selectedBefore: Date | undefined = $state();

    let largerThanInput: HTMLInputElement;
    let largerThanUnit: Size | undefined = $state();
    let smallerThanInput: HTMLInputElement;
    let smallerThanUnit: Size | undefined = $state();

    $effect(() => {
        if (!isSimpleSearchHidden && searchMenu) {
            simpleSearchInput = searchMenu.querySelector(
                'input[id="simple-search"]',
            )!;
        }

        if (!isExtraOptionsHidden && extraOptionsWrapper) {
            largerThanInput = extraOptionsWrapper.querySelector(
                'input[id="larger-than"]',
            )!;
            smallerThanInput = extraOptionsWrapper.querySelector(
                'input[id="smaller-than"]',
            )!;
        }
    });

    let standardFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].standard
            : [],
    );
    let customFolders: string[] = $derived(
        SharedStore.currentAccount !== "home"
            ? SharedStore.folders[
                  (SharedStore.currentAccount as Account).email_address
              ].custom
            : [],
    );

    let searchingAccount: typeof SharedStore.currentAccount = $state(
        SharedStore.currentAccount,
    );

    const search = async (): Promise<void> => {
        if (!isSimpleSearchHidden && isExtraOptionsHidden && simpleSearchInput.value.length < 3)
            return;

        const accounts =
            searchingAccount === "home"
                ? SharedStore.accounts
                : [SharedStore.currentAccount as Account];

        const results = await Promise.allSettled(
            accounts.map(async (account) => {
                const response = await MailboxController.getMailbox(
                    account,
                    searchingFolder,
                    isExtraOptionsHidden
                        ? simpleSearchInput.value
                        : isObjEmpty(searchCriteria)
                          ? searchCriteria
                          : undefined,
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

    const debouncedSearch = debounce((e: Event) => {
        search();
    }, REALTIME_SEARCH_DELAY_MS);

    const toggleSimpleSearch = () => {
        isSimpleSearchHidden = !isSimpleSearchHidden;
    };

    const toggleExtraOptions = () => {
        isExtraOptionsHidden = !isExtraOptionsHidden;
    };

    const selectSearchingAccount = (selectedAccount: string) => {
        searchingAccount =
            selectedAccount === "home"
                ? selectedAccount
                : SharedStore.accounts.find(
                      (acc) => acc.email_address === selectedAccount,
                  )!;
    };

    const selectFolder = (selectedFolder: string | Folder) => {
        searchingFolder = selectedFolder;
    };

    const addSender = (e: Event) => {
        if (!searchCriteria.senders) searchCriteria.senders = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="searching-senders"]')!;
        addEmailToAddressList(e, targetInput, searchCriteria.senders);
    };

    const addReceiver = (e: Event) => {
        if (!searchCriteria.receivers) searchCriteria.receivers = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>(
                'input[id="searching-receivers"]',
            )!;
        addEmailToAddressList(e, targetInput, searchCriteria.receivers);
    };

    const addCc = (e: Event) => {
        if (!searchCriteria.cc) searchCriteria.cc = [];
        const targetInput = (e.target as HTMLElement)
            .closest(".form-group")!
            .querySelector<HTMLInputElement>('input[id="searching-cc"]')!;
        addEmailToAddressList(e, targetInput, searchCriteria.cc);
    };

    const setSubject = (e: Event): void => {
        searchCriteria.subject = (e.target as HTMLInputElement).value;
    };

    const setSince = (selectedDate: Date) => {
        selectedSince = selectedDate;
        searchCriteria.since = convertToIMAPDate(selectedSince);
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedBefore.setDate(selectedSince.getDate() + 1);
        }
    };

    const setBefore = (selectedDate: Date) => {
        selectedBefore = selectedDate;
        searchCriteria.before = convertToIMAPDate(selectedBefore);
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedSince.setDate(selectedBefore.getDate() - 1);
        }
    };

    const setInclude = (e: Event): void => {
        searchCriteria.include = (e.target as HTMLInputElement).value;
    };

    const setExclude = (e: Event): void => {
        searchCriteria.exclude = (e.target as HTMLInputElement).value;
    };

    const addIncludedFlag = (flag: Mark) => {
        if (!searchCriteria.included_flags) searchCriteria.included_flags = [];
        if (searchCriteria.excluded_flags?.includes(flag))
            searchCriteria.excluded_flags =
                searchCriteria.excluded_flags.filter(
                    (excluded_flag) => excluded_flag !== flag,
                );
        searchCriteria.included_flags.push(flag);
    };

    const addExcludedFlag = (flag: Mark) => {
        if (!searchCriteria.excluded_flags) searchCriteria.excluded_flags = [];
        if (searchCriteria.included_flags?.includes(flag))
            searchCriteria.included_flags =
                searchCriteria.included_flags.filter(
                    (included_flag) => included_flag !== flag,
                );
        searchCriteria.excluded_flags.push(flag);
    };

    function updateSizes() {
        if (smallerThanInput.value && smallerThanUnit) {
            searchCriteria.smaller_than = convertSizeToBytes(
                concatValueAndUnit(smallerThanInput.value, smallerThanUnit),
            );
        }
        if (largerThanInput.value && largerThanUnit) {
            searchCriteria.larger_than = convertSizeToBytes(
                concatValueAndUnit(largerThanInput.value, largerThanUnit),
            );
        }
    }

    const setLargerThanUnit = (selectedLargerThanUnit: string) => {
        largerThanUnit = selectedLargerThanUnit as Size;
        updateSizes();
    };

    const setSmallerThanUnit = (selectedSmallerThanUnit: string) => {
        smallerThanUnit = selectedSmallerThanUnit as Size;
        updateSizes();
    };

    const setEnteredSize = (e: Event): void => {
        if (!smallerThanUnit || !largerThanUnit) return;

        const adjustedSizes = adjustSizes(
            [Number(smallerThanInput.value), smallerThanUnit],
            [Number(largerThanInput.value), largerThanUnit],
        );

        smallerThanInput.value = adjustedSizes[0][0].toString();
        smallerThanUnit = adjustedSizes[0][1] as Size;

        largerThanInput.value = adjustedSizes[1][0].toString();
        largerThanUnit = adjustedSizes[1][1] as Size;
        updateSizes();
    };

    const setHasAttachments = (e: Event) => {
        searchCriteria.has_attachments = (e.target as HTMLInputElement).checked;
    };

    const clear = () => {
        searchCriteria = {};
    };
</script>

<Button.Basic
    type="button"
    class="btn-outline nav-button"
    onclick={toggleSimpleSearch}
>
    <Icon name="search" />
</Button.Basic>

{#if !isSimpleSearchHidden}
<div class="modal" style="display:none"></div> <!-- to trigger modal overlay -->
<div class="search-menu modal-like" bind:this={searchMenu} transition:fade={{duration: 100}}>
    <Input.Group class="simple-search-input-group">
        <Button.Action type="button" onclick={search}>
            <Icon name="search" />
        </Button.Action>
        <Input.Basic
            type="text"
            id="simple-search"
            placeholder={getSearchForAccountTemplate(
                searchingAccount !== "home"
                    ? createSenderAddress(
                        searchingAccount.email_address,
                        searchingAccount.fullname
                    )
                    : searchingAccount,
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
    <div
        class="search-extra-options {isExtraOptionsHidden ? 'hidden' : ''}"
        bind:this={extraOptionsWrapper}
    >
        <FormGroup>
            <!-- Account -->
            <Label for="searching-account">{local.searching_account[DEFAULT_LANGUAGE]}</Label>
            <Select.Root
                id="searching-account"
                class="searching-account"
                value={SharedStore.currentAccount === "home"
                    ? "home"
                    : SharedStore.currentAccount.email_address}
                onchange={selectSearchingAccount}
            >
                <Select.Option
                    value="home"
                    content={local.home[DEFAULT_LANGUAGE]}
                />
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
            <!-- Account end -->
        </FormGroup>
        {#if SharedStore.currentAccount !== "home"}
            <FormGroup>
                <!-- Folder -->
                <Label for="searching-folder">{local.folder[DEFAULT_LANGUAGE]}</Label>
                <Select.Root
                    id="searching-folder"
                    value={Folder.All}
                    onchange={selectFolder}
                >
                    {#each standardFolders as standardFolder}
                        {@const [folderTag, folderName] =
                            standardFolder.split(":")}
                        <Select.Option
                            value={folderTag}
                            content={folderName}
                        />
                    {/each}
                    <Select.Separator />
                    {#each customFolders as customFolder}
                        <Select.Option
                            value={customFolder}
                            content={customFolder}
                        />
                    {/each}
                </Select.Root>
                <!-- Folder end -->
            </FormGroup>
        {/if}
        <FormGroup>
            <!-- Senders -->
            <Label for="searching-senders">{local.sender_s[DEFAULT_LANGUAGE]}</Label>
            <Input.Group>
                <Input.Basic
                    type="email"
                    id="searching-senders"
                    placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
                    onkeyup={addSender}
                    onblur={addSender}
                />
                <Button.Basic type="button" onclick={addSender}>
                    <Icon name="add" />
                </Button.Basic>
            </Input.Group>
            <div class="tags">
                {#if searchCriteria.senders}
                    {#each searchCriteria.senders as sender}
                        <Badge
                            content={sender}
                            onclick={() => {
                                searchCriteria.senders =
                                    searchCriteria.senders!.filter(
                                        (addr) => addr !== sender,
                                    );
                            }}
                        />
                    {/each}
                {/if}
            </div>
            <!-- Senders end -->
        </FormGroup>
        <FormGroup>
            <!-- Receivers -->
            <Label for="searching-receivers">{local.receiver_s[DEFAULT_LANGUAGE]}</Label>
            <Input.Group>
                <Input.Basic
                    type="email"
                    id="searching-receivers"
                    placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
                    onkeyup={addReceiver}
                    onblur={addReceiver}
                />
                <Button.Basic type="button" onclick={addReceiver}>
                    <Icon name="add" />
                </Button.Basic>
            </Input.Group>
            <div class="tags">
                {#if searchCriteria.receivers}
                    {#each searchCriteria.receivers as receiver}
                        <Badge
                            content={receiver}
                            onclick={() => {
                                searchCriteria.receivers =
                                    searchCriteria.receivers!.filter(
                                        (addr) => addr !== receiver,
                                    );
                            }}
                        />
                    {/each}
                {/if}
            </div>
            <!-- Receivers end -->
        </FormGroup>
        <FormGroup>
            <!-- Cc -->
            <Label for="searching-cc">{local.cc[DEFAULT_LANGUAGE]}</Label>
            <Input.Group>
                <Input.Basic
                    type="email"
                    id="searching-cc"
                    placeholder={local.add_email_address_with_space_placeholder[DEFAULT_LANGUAGE]}
                    onkeyup={addCc}
                    onblur={addCc}
                />
                <Button.Basic type="button" onclick={addCc}>
                    <Icon name="add" />
                </Button.Basic>
            </Input.Group>
            <div class="tags">
                {#if searchCriteria.cc}
                    {#each searchCriteria.cc as cc}
                        <Badge
                            content={cc}
                            onclick={() => {
                                searchCriteria.cc = searchCriteria.cc!.filter(
                                    (addr) => addr !== cc,
                                );
                            }}
                        />
                    {/each}
                {/if}
            </div>
            <!-- Cc end -->
        </FormGroup>
        <FormGroup>
            <!-- Subject -->
            <Label for="searching-subject">{local.subject[DEFAULT_LANGUAGE]}</Label>
            <Input.Basic
                type="text"
                id="searching-subject"
                placeholder={local.subject_placeholder[DEFAULT_LANGUAGE]}
                onkeydown={setSubject}
            />
            <!-- Subject end -->
        </FormGroup>
        <FormGroup>
            <!-- Range -->
            <Label>{local.date_range[DEFAULT_LANGUAGE]}</Label>
            <FormGroup direction="horizontal">
                <FormGroup style="width:100%">
                    <!-- Since -->
                    <Label for="since">{local.since[DEFAULT_LANGUAGE]}</Label>
                    <Input.Date
                        id="since"
                        value={selectedSince}
                        onchange={setSince}
                    />
                    <!-- Since end -->
                </FormGroup>
                <FormGroup style="width:100%">
                    <!-- Before -->
                    <Label for="before">{local.before[DEFAULT_LANGUAGE]}</Label>
                    <Input.Date
                        id="before"
                        value={selectedBefore}
                        onchange={setBefore}
                    />
                    <!-- Before end -->
                </FormGroup>
            </FormGroup>
            <!-- Range end -->
        </FormGroup>
        <FormGroup>
            <!-- Include -->
            <Label for="searching-include">{local.includes[DEFAULT_LANGUAGE]}</Label>
            <Input.Basic
                type="text"
                id="searching-include"
                placeholder={local.includes_placeholder[DEFAULT_LANGUAGE]}
                onkeydown={setInclude}
            />
            <!-- Include end -->
        </FormGroup>
        <FormGroup>
            <!-- Exclude -->
            <Label for="searching-exclude">{local.excludes[DEFAULT_LANGUAGE]}</Label>
            <Input.Basic
                type="text"
                id="searching-exclude"
                placeholder={local.excludes_placeholder[DEFAULT_LANGUAGE]}
                onkeydown={setExclude}
            />
            <!-- Exclude end -->
        </FormGroup>
        <FormGroup>
            <!-- Flags -->
            <Label>{local.flags[DEFAULT_LANGUAGE]}</Label>
            <FormGroup direction="horizontal">
                <FormGroup class="flag-group">
                    <!-- Included Flags -->
                    <Label for="included-flags">{local.included_flags[DEFAULT_LANGUAGE]}</Label>
                    <FormGroup direction="horizontal">
                        <Select.Root
                            id="included-flags"
                            placeholder="Include Flag"
                            style="width:100%"
                            resetAfterSelect={true}
                        >
                            {#each Object.entries(Mark) as mark}
                                <Select.Option
                                    value={mark[1]}
                                    content={mark[0]}
                                />
                            {/each}
                        </Select.Root>
                        <Button.Basic
                            type="button"
                            class="btn-inline"
                            onclick={addIncludedFlag}
                        >
                            <Icon name="add" />
                        </Button.Basic>
                    </FormGroup>
                    <div class="tags">
                        {#if searchCriteria.included_flags}
                            {#each searchCriteria.included_flags as included_flag}
                                <Badge content={included_flag} />
                            {/each}
                        {/if}
                    </div>
                    <!-- Included Flags end -->
                </FormGroup>
                <FormGroup class="flag-group">
                    <!-- Excluded Flags -->
                    <Label for="excluded-flags">{local.excluded_flags[DEFAULT_LANGUAGE]}</Label>
                    <FormGroup direction="horizontal">
                        <Select.Root
                            id="excluded-flags"
                            placeholder="Exclude Flag"
                            style="width:100%"
                            resetAfterSelect={true}
                        >
                            {#each Object.entries(Mark) as mark}
                                <Select.Option
                                    value={mark[1]}
                                    content={mark[0]}
                                />
                            {/each}
                        </Select.Root>
                        <Button.Basic
                            type="button"
                            class="btn-inline"
                            onclick={addExcludedFlag}
                        >
                            <Icon name="add" />
                        </Button.Basic>
                    </FormGroup>
                    <div class="tags">
                        {#if searchCriteria.excluded_flags}
                            {#each searchCriteria.excluded_flags as excluded_flag}
                                <Badge content={excluded_flag} />
                            {/each}
                        {/if}
                    </div>
                    <!-- Excluded Flags end -->
                </FormGroup>
            </FormGroup>
            <!-- Flags end -->
        </FormGroup>
        <FormGroup>
            <!-- Size -->
            <Label>{local.size[DEFAULT_LANGUAGE]}</Label>
            <FormGroup direction="horizontal">
                <FormGroup>
                    <!-- Larger than -->
                    <Label for="larger-than">{local.larger_than[DEFAULT_LANGUAGE]}</Label>
                    <FormGroup direction="horizontal" class="size-group">
                        <Input.Basic
                            type="number"
                            id="larger-than"
                            placeholder={local.larger_than_placeholder[DEFAULT_LANGUAGE]}
                            onkeydown={setEnteredSize}
                            />
                        <Select.Root
                            placeholder={Size.KB}
                            value={largerThanUnit}
                            onchange={setLargerThanUnit}
                        >
                            {#each Object.entries(Size) as size}
                                <Select.Option
                                    value={size[0]}
                                    content={size[1]}
                                />
                            {/each}
                        </Select.Root>
                    </FormGroup>
                    <!-- Larger than end -->
                </FormGroup>
                <FormGroup>
                    <!-- Smaller than -->
                    <Label for="smaller-than">{local.smaller_than[DEFAULT_LANGUAGE]}</Label>
                    <FormGroup direction="horizontal" class="size-group">
                        <Input.Basic
                            type="number"
                            id="smaller-than"
                            placeholder={local.smaller_than_placeholder[DEFAULT_LANGUAGE]}
                            onkeydown={setEnteredSize}
                        />
                        <Select.Root
                            placeholder={Size.MB}
                            value={smallerThanUnit}
                            onchange={setSmallerThanUnit}
                        >
                            {#each Object.entries(Size) as size}
                                <Select.Option
                                    value={size[0]}
                                    content={size[1]}
                                />
                            {/each}
                        </Select.Root>
                    </FormGroup>
                    <!-- Smaller than end -->
                </FormGroup>
            </FormGroup>
            <!-- Size end -->
        </FormGroup>
        <FormGroup direction="horizontal">
            <!-- Has attachments -->
            <Input.Basic
                type="checkbox"
                id="has-attachments"
                onchange={setHasAttachments}
            />
            <Label for="has-attachments">{local.has_attachments[DEFAULT_LANGUAGE]}</Label>
            <!-- Has attachments end -->
        </FormGroup>
        <FormGroup direction="horizontal" class="search-button-group">
            <Button.Basic type="button" class="btn-inline" onclick={clear}>
                <Icon name="trash" />
            </Button.Basic>
            <Button.Action type="button" class="btn-outline" onclick={search}>
                <Icon name="search" />
                <span>{local.search[DEFAULT_LANGUAGE]}</span>
            </Button.Action>
        </FormGroup>
    </div>
</div>
{/if}

<style>
    :global {
        .search-menu {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            width: var(--container-md);
            z-index: var(--z-index-modal);
            background-color: var(--color-bg-primary);
            border: 1px solid var(--color-border-subtle);
            border-radius: var(--radius-lg);

            & .simple-search-input-group{
                padding: 0 var(--spacing-sm);
                border-color: transparent!important;
            }

            & .search-extra-options {
                display: flex;
                flex-direction: column;
                height: var(--container-md);
                overflow-y: scroll!important;
                overflow-x: hidden;
                z-index: var(--z-index-modal);
                padding: var(--spacing-md);
                padding-right: calc(var(--spacing-md) + 5px); /* because of scrollbar */
                background-color: var(--color-bg-primary);
                border-bottom-left-radius: var(--radius-lg);
                border-bottom-right-radius: var(--radius-lg);
                border-top: 1px solid var(--color-border-subtle);

                & .size-group {
                    align-items: end;
                    font-size: var(--font-size-xs);
                    gap: var(--spacing-sm);
                }

                & .flag-group {
                    width: 100%;

                    & label + .form-group-horizontal {
                        gap: var(--spacing-md);
                    }
                }

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
