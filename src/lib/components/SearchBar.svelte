<script lang="ts">
    import { onMount } from "svelte";
    import { mount, unmount } from "svelte";
    import { SharedStore } from "$lib/stores/shared.svelte";
    import Loader from "$lib/components/Loader.svelte";
    import { ApiService } from "$lib/services/ApiService";
    import { GetRoutes } from "$lib/services/ApiService";
    import { Folder, Mark, type SearchCriteria } from "$lib/types";
    import { addDays, debounce } from "$lib/utils";

    let isAdvancedSearchMenuOpen = false;
    onMount(() => {});

    function toggleAdvancedSearchMenu() {
        isAdvancedSearchMenuOpen = !isAdvancedSearchMenuOpen;
    }

    function handleTagEnter(e: KeyboardEvent) {
        const target = e.target as HTMLInputElement;
        const tags = target
            .closest(".form-group")!
            .querySelector(".tags")! as HTMLElement;
        const isEmailValid = target.value.match(
            /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/,
        );
        if (e.key === "Spacebar" || e.key === " ") {
            if (target.value !== "" && isEmailValid) {
                tags.style.display = "flex";
                tags.innerHTML += `<span class="tag"><span class="value">${target.value}</span><button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button></span>`;
                target.value = "";
            } else {
                target.style.transform = "scale(1.02)";
                setTimeout(() => {
                    target.style.transform = "scale(1)";
                }, 100);
            }
        }
    }

    const handleSize = debounce((e: Event) => {
        const target = e.target as HTMLInputElement;
        const row = target.closest(".row")!;

        const smallerThan = row.querySelector(
            'input[name="smaller_than"]',
        ) as HTMLInputElement;
        const smallerThanValue = Number(smallerThan.value);

        const largerThan = row.querySelector(
            'input[name="larger_than"]',
        ) as HTMLInputElement;
        const largerThanValue = Number(largerThan.value);

        const smallerThanUnit = row.querySelector(
            'select[name="smaller_than_unit"]',
        ) as HTMLInputElement;
        const largerThanUnit = row.querySelector(
            'select[name="larger_than_unit"]',
        ) as HTMLInputElement;

        smallerThan.value = smallerThanValue < 0 ? "0" : smallerThan.value;
        largerThan.value = largerThanValue < 0 ? "0" : largerThan.value;

        if (smallerThanUnit.value === largerThanUnit.value) {
            if (smallerThanValue <= largerThanValue) {
                if (target == smallerThan)
                    largerThan.value = (smallerThanValue - 1).toString();
                else smallerThan.value = (largerThanValue + 1).toString();
            }
        } else {
            // Convert both of them to MB
            let smallerThanValueMb = smallerThanValue;
            if (smallerThanUnit.value === "kb") {
                smallerThanValueMb = smallerThanValueMb / 1024;
            } else if (smallerThanUnit.value === "gb") {
                smallerThanValueMb = smallerThanValueMb * 1024;
            }

            let largerThanValueMb = largerThanValue;
            if (largerThanUnit.value === "kb") {
                largerThanValueMb = largerThanValueMb / 1024;
            } else if (largerThanUnit.value === "gb") {
                largerThanValueMb = largerThanValueMb * 1024;
            }

            if (smallerThanValueMb < largerThanValueMb) {
                if (target == smallerThan || target == smallerThanUnit) {
                    largerThan.value = (smallerThanValue - 1).toString();
                    largerThanUnit.value = smallerThanUnit.value;
                } else {
                    smallerThan.value = (largerThanValue + 1).toString();
                    smallerThanUnit.value = largerThanUnit.value;
                }
            }
        }
    }, 100);

    function clearInput(e: Event) {
        const target = e.target as HTMLButtonElement;
        const inputGroup = target.closest(".input-group")!;

        const targetInputs = inputGroup.querySelectorAll(
            "input",
        ) as NodeListOf<HTMLInputElement>;
        targetInputs.forEach((input: HTMLInputElement) => {
            if (input.type === "number") input.value = "0";
            else input.value = "";
        });

        const targetSelects = inputGroup.querySelectorAll(
            "select",
        ) as NodeListOf<HTMLSelectElement>;
        targetSelects.forEach((select: HTMLSelectElement) => {
            select.selectedIndex = 0;
        });
    }

    function handleDate(e: Event) {
        const target = e.target as HTMLInputElement;
        const row = target.closest(".row")!;

        const since = row.querySelector(
            'input[name="since"]',
        ) as HTMLInputElement;
        const before = row.querySelector(
            'input[name="before"]',
        ) as HTMLInputElement;

        if (since.value !== "" && before.value !== "") {
            if (since.value > before.value) {
                if (target == since) before.value = addDays(since.value, 1);
                else since.value = addDays(before.value, -1);
            }
        }
    }

    function handleSelect(e: Event) {
        const target = e.target as HTMLButtonElement;
        const formGroup = target.closest(".form-group")!;
        const select = formGroup.querySelector("select") as HTMLSelectElement;
        const tags = formGroup.querySelector(".tags") as HTMLDivElement;
        if (select.value !== "") {
            tags.innerHTML += `<span class="tag"><span class="value">${select.value}</span><button type="button" style="margin-left:5px;" onclick="this.parentElement.remove()">X</button></span>`;
            select.selectedIndex = 0;
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
            subject: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="subject"]',
            )!.value,
            since: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="since"]',
            )!.value,
            before: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="before"]',
            )!.value,
            smaller_than: parseInt(
                advancedSearchMenu.querySelector<HTMLInputElement>(
                    'input[name="smaller_than"]',
                )!.value,
            ),
            larger_than: parseInt(
                advancedSearchMenu.querySelector<HTMLInputElement>(
                    'input[name="larger_than"]',
                )!.value,
            ),
            include: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="include"]',
            )!.value,
            exclude: advancedSearchMenu.querySelector<HTMLInputElement>(
                'input[name="exclude"]',
            )!.value,
            included_flags: extractAsArray("#saved-flags"),
            has_attachments:
                advancedSearchMenu.querySelector<HTMLInputElement>(
                    'input[name="has_attachments"]:checked',
                )!.checked
        };

        const isSearchCriteriaEmpty = Object.values(searchCriteria).every(
            (value) => {
                if (typeof value === "string") return value === "";
                if (Array.isArray(value)) return value.length === 0;
                if (typeof value === "boolean") return value === false;
            },
        );

        if (isSearchCriteriaEmpty) return null;

        return searchCriteria;
    }

    async function handleSearch(e: Event) {
        e.preventDefault();

        const eventButton = e.target as HTMLButtonElement;
        eventButton.disabled = true;
        const temp = eventButton.innerText;
        eventButton.innerText = "";
        const loader = mount(Loader, { target: eventButton });

        let searchCriteria: SearchCriteria | string | undefined = undefined;
        let folder: string = Folder.All;
        if(isAdvancedSearchMenuOpen) {
            searchCriteria = JSON.stringify(getSearchCriteria());
            folder = document.querySelector<HTMLSelectElement>(
                "#advanced-search-menu #folder",
            )!.value;
        } else {
            searchCriteria = document.querySelector<HTMLInputElement>(
                "#simple-search-input",
            )?.value;
        }

        const response = await ApiService.get(
            SharedStore.server,
            GetRoutes.GET_MAILBOXES,
            {
                pathParams: {
                    accounts: SharedStore.accounts
                        .map((account) => account.email_address)
                        .join(","),
                },
                queryParams: {
                    folder: folder,
                    search: searchCriteria,
                },
            },
        );

        if (response.success && response.data) {
            SharedStore.mailboxes = response.data;
            SharedStore.currentFolder = response.data[0].result.folder;
        } else {
            alert(response.message);
        }

        eventButton.disabled = false;
        eventButton.innerText = temp;
        unmount(loader);
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
                <select name="folder" id="folder">
                    <option value="{Folder.All}" selected>All</option>
                    {#each SharedStore.folders[0].result as folder}
                        <option value={folder}>{folder}</option>
                    {/each}
                </select>
                <button type="button" onclick={clearInput}>X</button>
            </div>
        </div>
        <div class="form-group">
            <label for="senders">Sender(s)</label>
            <input type="email" name="senders" onkeyup={handleTagEnter} placeholder="someone@domain.xyz" />
            <div class="tags" id="saved-senders"></div>
        </div>
        <div class="form-group">
            <label for="receivers">Receiver(s)</label>
            <input type="email" name="receivers" onkeyup={handleTagEnter} placeholder="someone@domain.xyz" />
            <div class="tags" id="saved-receivers"></div>
        </div>
        <div class="form-group">
            <label for="cc">Cc</label>
            <input type="email" name="cc" id="cc" onkeyup={handleTagEnter} placeholder="someone@domain.xyz" />
            <div class="tags" id="saved-cc"></div>
        </div>
        <div class="form-group">
            <label for="bcc">Bcc</label>
            <input type="email" name="bcc" id="bcc" onkeyup={handleTagEnter} placeholder="someone@domain.xyz" />
            <div class="tags" id="saved-bcc"></div>
        </div>
        <div class="form-group">
            <label for="subject">Subject</label>
            <input type="text" name="subject" placeholder="Subject" />
            <div class="tags"></div>
        </div>
        <div class="row">
            <div class="form-group">
                <label for="since">Since</label>
                <div class="input-group">
                    <input type="date" name="since" onchange={handleDate} />
                    <button type="button" onclick={clearInput}>X</button>
                </div>
            </div>
            <div class="form-group">
                <label for="before">Before</label>
                <div class="input-group">
                    <input type="date" name="before" onchange={handleDate} />
                    <button type="button" onclick={clearInput}>X</button>
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
                        onkeyup={handleSize}
                    />
                    <select name="smaller_than_unit" onchange={handleSize}>
                        <option value="kb" selected>KB</option>
                        <option value="mb">MB</option>
                        <option value="gb">GB</option>
                    </select>
                    <button type="button" onclick={clearInput}>X</button>
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
                        onkeyup={handleSize}
                    />
                    <select name="larger_than_unit" onchange={handleSize}>
                        <option value="kb">KB</option>
                        <option value="mb">MB</option>
                        <option value="gb">GB</option>
                    </select>
                    <button type="button" onclick={clearInput}>X</button>
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
            <label for="includes-flags">Include Flag</label>
            <div class="input-group">
                <select name="includes-flags" id="includes-flags">
                    {#each Object.entries(Mark) as mark}
                        <option value={mark[1]}>{mark[0]}</option>
                    {/each}
                </select>
                <button type="button" onclick={handleSelect}>+</button>
            </div>
            <div class="tags" id="saved-flags">
                <!-- Flags -->
            </div>
        </div>
    </div>
    <button type="button" style="margin-top:5px;" onclick={handleSearch}
        >Search</button
    >
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
