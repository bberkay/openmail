<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import { Folder, Mark, type Account, type SearchCriteria } from "$lib/types";
    import { debounce, isEmailValid, adjustSizes, convertToIMAPDate, concatValueAndUnit, convertSizeToBytes, isObjEmpty } from "$lib/utils";
    import { Size } from "$lib/utils/types";
    import * as Select from "$lib/ui/Elements/Select";
    import * as Button from "$lib/ui/Elements/Button";
    import * as Input from "$lib/ui/Elements/Input";

    /* Constants */

    const mailboxController = new MailboxController();
    const tagTemplate = `
        <span class="tag">
            <span class="value">{tag}</span>
            <button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button>
        </span>
    `;

    /* Variables */

    let advancedSearchMenu: HTMLElement;
    let simpleSearchInput: HTMLInputElement;

    let folder: string | undefined = $state(Folder.All);
    let isAdvancedSearchMenuOpen = $state(false);
    let selectedSince: Date | undefined = $state(undefined);
    let selectedBefore: Date | undefined = $state(undefined);
    let smallerThanUnit: string | undefined = $state(undefined);
    let largerThanUnit: string | undefined = $state(undefined);

    /* Criteria Handling Functions */

    const addSelectedAccount = (selectedAccount: string | null) => {
        const tags = document.getElementById("added-accounts") as HTMLDivElement;
        if (selectedAccount) {
            tags.innerHTML += tagTemplate.replace("{tag}", selectedAccount);
        }
    }

    const setSelectedFolder = (selectedFolder: string | null) => {
        if (selectedFolder) {
            folder = selectedFolder;
        }
    }

    const addEnteredEmail = (e: Event) => {
        const target = e.target as HTMLInputElement;
        const email_address = target.value.trim();
        const emails = target.closest(".form-group")?.querySelector(".emails") as HTMLElement;

        if (!emails) return;

        if (e instanceof KeyboardEvent && (e.key === " " || e.key === "Spacebar")) {
            e.preventDefault();
            processEmail(target, emails, email_address);
        }
        else if (e instanceof FocusEvent) {
            processEmail(target, emails, email_address);
        }
    };

    function processEmail(target: HTMLInputElement, emails: HTMLElement, email_address: string) {
        if (email_address !== "" && isEmailValid(email_address)) {
            emails.style.display = "flex";
            emails.innerHTML += tagTemplate.replace("{tag}", email_address);
            target.value = "";
        } else if (email_address !== "") {
            target.style.transform = "scale(1.02)";
            setTimeout(() => {
                target.style.transform = "scale(1)";
            }, 100);
        }
    };

    const setEnteredSizeValue = debounce((e: Event) => {
        const target = e.target as HTMLInputElement;
        const row = target.closest(".row")!;

        if (!smallerThanUnit || !largerThanUnit)
            return;

        const smallerThanInput = row.querySelector(
            'input[name="smaller_than"]',
        ) as HTMLInputElement;

        const largerThanInput = row.querySelector(
            'input[name="larger_than"]',
        ) as HTMLInputElement;

        const adjustedSizes = adjustSizes(
            [
                Number(smallerThanInput.value),
                smallerThanUnit as Size
            ],
            [
                Number(largerThanInput.value),
                largerThanUnit as Size
            ]
        );

        smallerThanInput.value = adjustedSizes[0][0].toString();
        smallerThanUnit = adjustedSizes[0][1]

        largerThanInput.value = adjustedSizes[1][0].toString();
        largerThanUnit = adjustedSizes[1][1]
    }, 100);

    const setSelectedSmallerThanUnit = (selectedUnit: string | null) => {
        smallerThanUnit = selectedUnit || undefined;
    }

    const setSelectedLargerThanUnit = (selectedUnit: string | null) => {
        largerThanUnit = selectedUnit || undefined;
    }

    const setSelectedSinceDate = (selectedDate: Date) => {
        selectedSince = selectedDate;
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedBefore.setDate(selectedSince.getDate() + 1)
        }
    }

    const setSelectedBeforeDate = (selectedDate: Date) => {
        selectedBefore = selectedDate;
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedSince.setDate(selectedBefore.getDate() - 1)
        }
    }

    const addIncludedFlag = (selectedFlag: string | null) => {
        const tags = document.getElementById("search-included-flags") as HTMLDivElement;
        if (selectedFlag) {
            tags.innerHTML += tagTemplate.replace("{tag}", selectedFlag);
        }
    }

    const addExcludedFlag = (selectedFlag: string | null) => {
        const tags = document.getElementById("search-excluded-flags") as HTMLDivElement;
        if (selectedFlag) {
            tags.innerHTML += tagTemplate.replace("{tag}", selectedFlag);
        }
    }

    /* Search Criteria Creator Functions */

    function extractAsArray(selector: string): string[] {
        return Array.from<HTMLElement>(
            advancedSearchMenu
                .querySelector(selector)!
                .querySelectorAll("span.value"),
        ).map((span: HTMLElement) => {
            return span.textContent || "";
        });
    };

    function getSearchCriteria(): SearchCriteria | null {
        const searchCriteria: SearchCriteria = {
            senders: extractAsArray("#search-senders"),
            receivers: extractAsArray("#search-receivers"),
            cc: extractAsArray("#search-cc"),
            bcc: extractAsArray("#search-bcc"),
            included_flags: extractAsArray("#search-included-flags"),
            excluded_flags: extractAsArray("#search-excluded-flags"),
            subject: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="subject"]',
            )!.value,
            include: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="include"]',
            )!.value,
            exclude: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="exclude"]',
            )!.value,
            has_attachments:
                advancedSearchMenu.querySelector<HTMLInputElement>(
                    'input[name="has_attachments"]',
                )!.checked,
            since: selectedSince ? convertToIMAPDate(selectedSince) : undefined,
            before: selectedBefore ? convertToIMAPDate(selectedBefore) : undefined,
            smaller_than: smallerThanUnit ? convertSizeToBytes(concatValueAndUnit(advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="smaller_than"]',
            )!.value, smallerThanUnit as Size)) : undefined,
            larger_than: largerThanUnit ? convertSizeToBytes(concatValueAndUnit(advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="larger_than"]',
            )!.value, largerThanUnit as Size)) : undefined
        };

        if (isObjEmpty(searchCriteria))
            return null;

        return searchCriteria;
    }

    /* Main Operation */

    const search = async (): Promise<void> => {
        let searchCriteria: SearchCriteria | string | undefined = undefined;
        searchCriteria = isAdvancedSearchMenuOpen
            ? (getSearchCriteria() || undefined)
            : simpleSearchInput.value;

        const response = await mailboxController.getMailboxes(
            !isAdvancedSearchMenuOpen
                ? SharedStore.currentAccount
                : SharedStore.currentAccount,
                /*: (SharedStore.accounts.filter(
                    (account: Account) => {
                        return extractAsArray("#added-accounts").includes(account.email_address)
                    }
                ) || SharedStore.currentAccount),*/
            folder,
            searchCriteria
        );
        if (!response.success) {
            alert(response.message);
        }
    }
</script>

<div class="card" id="search-menu">
    <div class="input-group">
        <input type="text" style="width:100%" placeholder="Search" id="simple-search-input" bind:this={simpleSearchInput}/>
        <button type="button" onclick={() => { isAdvancedSearchMenuOpen = !isAdvancedSearchMenuOpen }}>⇅</button>
    </div>
    <div
        id="advanced-search-menu"
        class={isAdvancedSearchMenuOpen ? "open" : ""}
        bind:this={advancedSearchMenu}
    >
        <div class="form-group">
            <label for="accounts">Accounts</label>
            <div class="input-group" id="accounts">
                <Select.Menu onchange={addSelectedAccount} placeholder="Account(s) to Search" resetAfterSelect={true}>
                    {#each SharedStore.accounts as account}
                        <Select.Option value={account.email_address}>
                            {account.fullname} &lt;{account.email_address}&gt;
                        </Select.Option>
                    {/each}
                </Select.Menu>
            </div>
            <div class="tags" id="added-accounts">
                <!-- Accounts -->
            </div>
        </div>
        <div class="form-group">
            <label for="folder">Folder</label>
            <div class="input-group">
                <Select.Menu enableSearch={true} onchange={setSelectedFolder} value={Folder.All}>
                    {#each SharedStore.standardFolders[0].result as standardFolder}
                        {@const [folderTag, folderName] = standardFolder.split(":")}
                        <Select.Option value={folderTag}>{folderName}</Select.Option>
                    {/each}
                    {#each SharedStore.customFolders[0].result as customFolder}
                        <Select.Option value={customFolder}>{customFolder}</Select.Option>
                    {/each}
                </Select.Menu>
            </div>
        </div>
        <div class="form-group">
            <label for="senders">Sender(s)</label>
            <input type="email" name="senders" onkeyup={addEnteredEmail} onblur={addEnteredEmail} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="search-senders"></div>
        </div>
        <div class="form-group">
            <label for="receivers">Receiver(s)</label>
            <input type="email" name="receivers" onkeyup={addEnteredEmail} onblur={addEnteredEmail} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="search-receivers"></div>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" onkeyup={addEnteredEmail} onblur={addEnteredEmail} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="search-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" onkeyup={addEnteredEmail} onblur={addEnteredEmail} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="search-bcc"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" placeholder="Subject" />
        </div>
        <div class="row">
            <div class="form-group">
                <label for="since">Since</label>
                <div class="input-group">
                    <Input.Date
                        onchange={setSelectedSinceDate}
                        value={selectedSince}
                    />
                </div>
            </div>
            <div class="form-group">
                <label for="before">Before</label>
                <div class="input-group">
                    <Input.Date
                        onchange={setSelectedBeforeDate}
                        value={selectedBefore}
                    />
                </div>
            </div>
        </div>
        <div class="row">
            <div class="form-group">
                <label for="since">Smaller Than</label>
                <div class="input-group">
                    <input
                        type="number"
                        name="smaller_than"
                        min="0"
                        value="0"
                        onkeyup={setEnteredSizeValue}
                    />
                    <Select.Menu value={smallerThanUnit} onchange={setSelectedSmallerThanUnit}>
                        {#each Object.values(Size) as size}
                            <Select.Option value={size}>{size}</Select.Option>
                        {/each}
                    </Select.Menu>
                </div>
            </div>
            <div class="form-group">
                <label for="before">Larger Than</label>
                <div class="input-group">
                    <input
                        type="number"
                        name="larger_than"
                        min="0"
                        value="0"
                        onkeyup={setEnteredSizeValue}
                    />
                    <Select.Menu value={largerThanUnit} onchange={setSelectedLargerThanUnit}>
                        {#each Object.values(Size) as size}
                            <Select.Option value={size}>{size}</Select.Option>
                        {/each}
                    </Select.Menu>
                </div>
            </div>
        </div>
        <div class="form-group">
            <span style="margin-bottom:5px;">Has Attachment(s)</span>
            <div class="input-group">
                <input
                    type="checkbox"
                    name="has_attachments"
                    value="Yes"
                    id="has-attachments"
                />
                <label for="has-attachments">Yes</label>
            </div>
        </div>
        <div class="form-group">
            <label for="include">Includes</label>
            <input type="text" name="include" placeholder="What should be included" />
        </div>
        <div class="form-group">
            <label for="exclude">Excludes</label>
            <input type="text" name="exclude" placeholder="What should be excluded" />
        </div>
        <div class="form-group">
            <label for="included-flags">Include Flag</label>
            <div class="input-group" id="included-flags">
                <Select.Menu onchange={addIncludedFlag} placeholder="Flag" resetAfterSelect={true}>
                    {#each Object.entries(Mark) as mark}
                        <Select.Option value={mark[1]}>{mark[0]}</Select.Option>
                    {/each}
                </Select.Menu>
            </div>
            <div class="tags" id="search-included-flags">
                <!-- Flags -->
            </div>
        </div>
        <div class="form-group">
            <label for="excluded-flags">Exclude Flag</label>
            <div class="input-group" id="excluded-flags">
                <Select.Menu onchange={addExcludedFlag} placeholder="Flag" resetAfterSelect={true}>
                    {#each Object.entries(Mark) as mark}
                        <Select.Option value={mark[1]}>{mark[0]}</Select.Option>
                    {/each}
                </Select.Menu>
            </div>
            <div class="tags" id="search-excluded-flags">
                <!-- Flags -->
            </div>
        </div>
    </div>
    <Button.Action onclick={search} style="margin-top:5px;">
        Search
    </Button.Action>
</div>

<style>
    #advanced-search-menu {
        display: none;
        border: 1px solid #5a5a5a;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px #202020;
        background-color: #202020;

        &.open {
            display: flex;
            flex-direction: column;
        }

        & input + label,
        & label + input {
            margin-left: 5px;
        }
    }

    .row {
        display: flex;
        flex-direction: row;

        & > .form-group {
            flex-grow: 1;
        }

        & > .form-group + .form-group {
            margin-left: 5px;
        }
    }

    .input-group :first-child:not([type="checkbox"]) {
        flex-grow: 1;
    }

    .input-group :last-child {
        margin-left: 5px;
    }
</style>
