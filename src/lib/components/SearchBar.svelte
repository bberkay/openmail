<script lang="ts">
    import { SharedStore } from "$lib/stores/shared.svelte";
    import { Folder, Mark, type SearchCriteria } from "$lib/types";
    import { Size } from "$lib/utils/types";
    import { debounce, isEmailValid, adjustSizes, convertToIMAPDate, concatValueAndUnit, convertSizeToBytes, isObjEmpty } from "$lib/utils";
    import Select, { type Option } from "$lib/components/Elements/Select.svelte";
    import ActionButton from "$lib/components/Elements/ActionButton.svelte";
    import { MailboxController } from "$lib/controllers/MailboxController";
    import DatePicker from "$lib/components/Elements/DatePicker.svelte";

    const mailboxController = new MailboxController();

    let isAdvancedSearchMenuOpen = $state(false);
    let includeFlagSelectTrigger: boolean = $state(true);
    let selectedSince: Date | undefined = $state(undefined);
    let selectedBefore: Date | undefined = $state(undefined);
    let smallerThanUnit: Option | undefined = $state(undefined);
    let largerThanUnit: Option | undefined = $state(undefined);

    const tagTemplate = `
        <span class="tag">
            <span class="value">{tag}</span>
            <button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button>
        </span>
    `;

    const toggleAdvancedSearchMenu = () => {
        isAdvancedSearchMenuOpen = !isAdvancedSearchMenuOpen;
    }

    const handleEmailEnter = (e: KeyboardEvent) => {
        const target = e.target as HTMLInputElement;
        const email = target.value;
        const emails = target
            .closest(".form-group")!
            .querySelector(".emails")! as HTMLElement;
        if (e.key === "Spacebar" || e.key === " ") {
            if (email !== "" && isEmailValid(email)) {
                emails.style.display = "flex";
                emails.innerHTML += tagTemplate.replace("{tag}", email);
                target.value = "";
            } else {
                target.style.transform = "scale(1.02)";
                setTimeout(() => {
                    target.style.transform = "scale(1)";
                }, 100);
            }
        }
    }

    const handleSizeValue = debounce((e: Event) => {
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
                smallerThanUnit.value as Size
            ],
            [
                Number(largerThanInput.value),
                largerThanUnit.value as Size
            ]
        );

        smallerThanInput.value = adjustedSizes[0][0].toString();
        smallerThanUnit = {value: adjustedSizes[0][1], inner: adjustedSizes[0][1]};

        largerThanInput.value = adjustedSizes[1][0].toString();
        largerThanUnit = {value: adjustedSizes[1][1], inner: adjustedSizes[1][1]};
    }, 100);

    const handleSmallerThanUnit = (selectedUnit: string | null) => {
        smallerThanUnit = selectedUnit ? {value: selectedUnit, inner: selectedUnit} : undefined;
    }

    const handleLargerThanUnit = (selectedUnit: string | null) => {
        largerThanUnit = selectedUnit ? {value: selectedUnit, inner: selectedUnit} : undefined;
    }

    const handleSince = (selectedDate: Date) => {
        selectedSince = selectedDate;
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedBefore.setDate(selectedSince.getDate() + 1)
        }
    }

    const handleBefore = (selectedDate: Date) => {
        selectedBefore = selectedDate;
        if (selectedSince && selectedBefore && selectedSince > selectedBefore) {
            selectedSince.setDate(selectedBefore.getDate() - 1)
        }
    }

    const handleFlag = (selectedFlag: string | null) => {
        const tags = document.getElementById("saved-flags") as HTMLDivElement;
        if (selectedFlag) {
            tags.innerHTML += tagTemplate.replace("{tag}", selectedFlag);
            includeFlagSelectTrigger = !includeFlagSelectTrigger;
        }
    }

    function getSearchCriteria(): SearchCriteria | null {
        const advancedSearchMenu = document.getElementById(
            "advanced-search-menu",
        ) as HTMLDivElement;

        const extractAsArray = (selector: string) => {
            return Array.from(
                advancedSearchMenu
                    .querySelector(selector)!
                    .querySelectorAll("span.value"),
            ).map((span) => {
                return span.textContent || "";
            });
        };

        const searchCriteria: SearchCriteria = {
            senders: extractAsArray("#saved-senders"),
            receivers: extractAsArray("#saved-receivers"),
            cc: extractAsArray("#saved-cc"),
            bcc: extractAsArray("#saved-bcc"),
            included_flags: extractAsArray("#saved-flags"),
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
            )!.value, smallerThanUnit.value as Size)) : undefined,
            larger_than: largerThanUnit ? convertSizeToBytes(concatValueAndUnit(advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="larger_than"]',
            )!.value, largerThanUnit.value as Size)) : undefined
        };

        if (isObjEmpty(searchCriteria))
            return null;

        return searchCriteria;
    }

    const handleSearch = async (): Promise<void> => {
        let searchCriteria: SearchCriteria | string | undefined = undefined;
        let folder: string = Folder.All;
        if(isAdvancedSearchMenuOpen) {
            searchCriteria = getSearchCriteria() || undefined;
            folder = document.querySelector<HTMLSelectElement>(
                "#advanced-search-menu #folder",
            )!.value;
        } else {
            searchCriteria = document.querySelector<HTMLInputElement>(
                "#simple-search-input",
            )?.value;
        }

        const response = await mailboxController.searchEmails(folder, searchCriteria);
        if (!response.success) {
            alert(response.message);
        }
    }
</script>

<div class="card" id="search-menu">
    <div class="input-group">
        <input type="text" style="width:100%" placeholder="Search" id="simple-search-input"/>
        <button type="button" onclick={toggleAdvancedSearchMenu}>⇅</button>
    </div>
    <div
        id="advanced-search-menu"
        class={isAdvancedSearchMenuOpen ? "open" : ""}
    >
        <div class="form-group">
            <label for="folder">Folder</label>
            <div class="input-group">
                <Select
                    id="search-folder-select"
                    options={
                        SharedStore.standardFolders[0].result.map((standardFolder) => {
                            const [folderTag, folderName] = standardFolder.split(":")
                            return {value: folderTag, inner: folderName}
                        }).concat(SharedStore.customFolders[0].result.map(customFolder => (
                            {value: customFolder, inner: customFolder})
                        ))
                    }
                    value={{value: Folder.All, inner: "All"}}
                />
            </div>
        </div>
        <div class="form-group">
            <label for="senders">Sender(s)</label>
            <input type="email" name="senders" onkeyup={handleEmailEnter} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="saved-senders"></div>
        </div>
        <div class="form-group">
            <label for="receivers">Receiver(s)</label>
            <input type="email" name="receivers" onkeyup={handleEmailEnter} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="saved-receivers"></div>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" onkeyup={handleEmailEnter} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="saved-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" onkeyup={handleEmailEnter} placeholder="someone@domain.xyz" />
            <div class="tags emails" id="saved-bcc"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" placeholder="Subject" />
        </div>
        <div class="row">
            <div class="form-group">
                <label for="since">Since</label>
                <div class="input-group">
                    <DatePicker
                        id="since"
                        operation={handleSince}
                        value={selectedSince}
                    />
                </div>
            </div>
            <div class="form-group">
                <label for="before">Before</label>
                <div class="input-group">
                    <DatePicker
                        id="before"
                        operation={handleBefore}
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
                        onkeyup={handleSizeValue}
                    />
                    <Select
                        id="smallter-than-unit"
                        options={Object.values(Size).map(size => ({value: size, inner: size}))}
                        operation={handleSmallerThanUnit}
                        value={smallerThanUnit}
                    />
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
                        onkeyup={handleSizeValue}
                    />
                    <Select
                        id="larger-than-unit"
                        options={Object.values(Size).map(size => ({value: size, inner: size}))}
                        operation={handleLargerThanUnit}
                        value={largerThanUnit}
                    />
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
                    checked
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
            <label for="include-flags">Include Flag</label>
            <div class="input-group">
                <Select
                    id="include-flags"
                    options={Object.entries(Mark).map(mark => ({value: mark[1], inner: mark[0]}))}
                    operation={handleFlag}
                    placeholder='Flag'
                    value={includeFlagSelectTrigger ? {value:'', inner:''} : {value:'', inner:''}}
                />
            </div>
            <div class="tags" id="saved-flags">
                <!-- Flags -->
            </div>
        </div>
    </div>
    <ActionButton id="search-emails-btn" operation={handleSearch}  style="margin-top:5px;">
        Search
    </ActionButton>
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
