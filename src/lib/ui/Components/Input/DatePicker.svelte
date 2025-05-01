<script lang="ts">
    import { onMount } from "svelte";
    import { getDays, getMonths, convertToIMAPDate, combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import * as Input from "$lib/ui/Components/Input";
    import * as Table from "$lib/ui/Components/Table";

    interface Props {
        id?: string,
        placeholder?: string,
        value?: Date,
        onchange?: (selectedDay: Date) => void,
        [attribute: string]: unknown;
    }

    let {
        id,
        placeholder,
        value,
        onchange,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let currentDate = new Date();
    let currentYear = currentDate.getFullYear();
    let currentMonth = currentDate.getMonth();
    let displayedYear: number = $state(currentYear);
    let displayedMonth: number = $state(currentMonth);
    let selectedDate: Date | "" = $state(value || "");

    let isDatePickerOpen: boolean = $state(false);
    let datePickerWrapper: HTMLDivElement;
    let dateInput: HTMLInputElement;
    let calendarBody: HTMLElement;

    placeholder = placeholder ?? new Date().toLocaleDateString();
    onMount(() => {
        dateInput = datePickerWrapper.querySelector(".date-input")!;
        calendarBody = datePickerWrapper.querySelector(".calendar-body")!;
        if (datePickerWrapper) {
            renderCalendar();
        }
    });

    const closeWhenClickedOutside = (e: Event) => {
        if (
            !datePickerWrapper.contains(e.target as HTMLElement) &&
            e.target !== dateInput
        ) {
            isDatePickerOpen = false;
        }
    }

    function selectDate(selectedDayNumber: string) {
        selectedDate = new Date(
            displayedYear,
            displayedMonth,
            parseInt(selectedDayNumber),
        );
        const prevSelectedDate = calendarBody.querySelector(`.selected-date`);
        if (prevSelectedDate) prevSelectedDate.classList.remove("selected-date");
        calendarBody.querySelector(`td[data-date="${selectedDayNumber}"]`)!.classList.add("selected-date");
        isDatePickerOpen = false;
        if(onchange) onchange(selectedDate);
    }

    const goPrevMonth = () => {
        displayedMonth--;
        if (displayedMonth < 0) {
            displayedMonth = 11;
            displayedYear--;
        }
        renderCalendar();
    };

    const goNextMonth = () => {
        displayedMonth++;
        if (displayedMonth > 11) {
            displayedMonth = 0;
            displayedYear++;
        }
        renderCalendar();
    };

    const clearSelection = () => {
        selectedDate = "";
        dateInput.value = "";
        renderCalendar();
    }

    function renderCalendar() {
        const firstDay = new Date(displayedYear, displayedMonth, 1);
        const lastDay = new Date(displayedYear, displayedMonth + 1, 0);
        const startingDay = firstDay.getDay();
        const totalDays = lastDay.getDate();

        let html = "";
        let date = 1;

        for (let i = 0; i < 6; i++) {
            let row = "<tr>";

            for (let j = 0; j < 7; j++) {
                let displayedDay = date;

                const classes = [];
                if (i === 0 && j < startingDay) {
                    classes.push("other-month");
                    classes.push("prev-month");
                    const prevMonthLastDay = new Date(
                        displayedYear,
                        displayedMonth,
                        0,
                    ).getDate();
                    displayedDay = prevMonthLastDay - (startingDay - j - 1);
                    date--;
                } else if (date > totalDays) {
                    classes.push("other-month");
                    classes.push("next-month");
                    displayedDay = date - totalDays;
                }

                const isCurrentDate =
                    displayedDay === currentDate.getDate() &&
                    displayedMonth === currentDate.getMonth() &&
                    displayedYear === currentDate.getFullYear();

                const isSelectedDate =
                    selectedDate &&
                    displayedDay === selectedDate.getDate() &&
                    displayedMonth === selectedDate.getMonth() &&
                    displayedYear === selectedDate.getFullYear();

                classes.push("date");
                if (isCurrentDate) classes.push("current-date");
                if (isSelectedDate) classes.push("selected-date");

                row += `<td class="${classes.join(" ")}" data-date="${displayedDay}">${displayedDay}</td>`;
                date++;
            }

            row += "</tr>";
            html += row;

            if (date > totalDays && i !== 0) {
                break;
            }
        }

        calendarBody.innerHTML = html;

        // Add click event listeners to dates
        calendarBody
            .querySelectorAll<HTMLElement>("td[data-date]")
            .forEach((cell: HTMLElement) => {
                cell.addEventListener("click", () => {
                  if (cell.classList.contains("next-month")) {
                      goNextMonth();
                  } else if (cell.classList.contains("prev-month")) {
                      goPrevMonth();
                  }
                  selectDate(cell.dataset.date!);
                });
            });
    }
</script>

<svelte:body onclick={closeWhenClickedOutside} />

<div
    bind:this={datePickerWrapper}
    class={combine("date-input-wrapper", additionalClass)}
    {...restAttributes}
>
    <Input.Basic
        id={id}
        type="text"
        class="date-input"
        placeholder={convertToIMAPDate(placeholder)}
        value={selectedDate ? convertToIMAPDate(selectedDate) : ""}
        onclick={() => { isDatePickerOpen = !isDatePickerOpen }}
        readonly
    />
    <div class="datepicker-container {isDatePickerOpen ? 'visible' : ''}">
        <div class="datepicker-header">
            <div class="month-year-selector">
                <Button.Basic
                    class="btn-outline"
                    id="prev-month"
                    onclick={goPrevMonth}
                >←</Button.Basic>
                {getMonths()[displayedMonth]}
                {displayedYear}
                <Button.Basic
                    class="btn-outline"
                    id="next-month"
                    onclick={goNextMonth}
                >→</Button.Basic>
            </div>
            <Button.Basic
                class="btn-outline"
                onclick={clearSelection}
            >X</Button.Basic>
        </div>
        <Table.Root class="calendar">
            <Table.Header>
                <Table.Row>
                    {#each getDays() as day}
                      <Table.Head>{day}</Table.Head>
                    {/each}
                </Table.Row>
            </Table.Header>
            <Table.Body class="calendar-body">
                <br/>
            </Table.Body>
        </Table.Root>
    </div>
</div>

<style>
    :global {
        .date-input-wrapper{
            position: relative;

            & .datepicker-container {
                position: absolute;
                top: 100%;
                left: 0;
                width: max-content;
                border: 1px solid var(--color-border);
                border-radius: var(--radius-sm);
                border-top-left-radius: none;
                border-top-right-radius: none;
                padding: var(--spacing-sm);
                background: var(--color-bg-primary);
                z-index: var(--z-index-dropdown);
                opacity: 0;
                visibility: hidden;
                transition: all var(--transform-fast) var(--ease-default);
                box-shadow: var(--shadow-sm);

                & .datepicker-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--spacing-sm);

                    & .month-year-selector {
                        display: flex;
                        gap: var(--spacing-sm);
                        align-items: center;
                    }
                }
            }

            & .calendar {
                width: 100%;
                color: var(--color-text-primary);

                & th {
                    padding: var(--spacing-xs);
                    background: none;
                    color: var(--color-text-secondary);
                }

                & td {
                    padding: var(--spacing-xs);
                    text-align: center;
                    cursor: pointer;
                    position: relative;

                    &:hover {
                        background-color: var(--color-hover);
                    }

                    &.current-date {
                        background: var(--color-border-subtle);
                        border-radius: var(--radius-sm);
                    }

                    &.selected-date {
                        background: var(--color-text-primary);
                        color: var(--color-bg-primary);
                        border-radius: var(--radius-sm);
                    }

                    &.other-month {
                        color: var(--color-text-secondary);
                    }
                }
            }
        }
    }
</style>
