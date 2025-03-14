<script lang="ts">
    import { onMount } from "svelte";
    import * as Select from "$lib/ui/Elements/Select";
    import { getDays, getMonths, convertToIMAPDate, range } from "$lib/utils";

    interface Props {
        placeholder?: string,
        value?: Date,
        onchange?: (selectedDay: Date) => void,
    }

    let {
        placeholder,
        value,
        onchange
    }: Props = $props();
    
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
        calendarBody.querySelector(`td[data-date="${selectedDayNumber}"]`).classList.add("selected-date");
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

<div class="date-input-wrapper" bind:this={datePickerWrapper}>
    <input
        type="text"
        class="date-input"
        readonly
        placeholder={convertToIMAPDate(placeholder)}
        value={selectedDate ? convertToIMAPDate(selectedDate) : ""}
        bind:this={dateInput}
        onclick={() => { isDatePickerOpen = !isDatePickerOpen }}
    />
    <div class="datepicker-container {isDatePickerOpen ? 'visible' : ''}">
        <div class="datepicker-header">
            <div class="month-year-selector">
                <button class="nav-button" id="prev-month" onclick={goPrevMonth}>←</button>
                {getMonths()[displayedMonth]}
                {displayedYear}
                <button class="nav-button" id="next-month" onclick={goNextMonth}>→</button>
            </div>
            <button class="clear-button" onclick={clearSelection}>Clear</button>
        </div>
        <table class="calendar">
            <thead>
                <tr>
                  {#each getDays() as day}
                    <th>{day}</th>
                  {/each}
                </tr>
            </thead>
            <tbody id="calendar-body" bind:this={calendarBody}></tbody>
        </table>
    </div>
</div>

<style>
    .date-input-wrapper :global{
        position: relative;
        width: 200px;

        & .date-input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
        }

        & .datepicker-container {
            visibility: hidden;
            position: absolute;
            top: 100%;
            left: 0;
            width: 300px;
            font-family: Arial, sans-serif;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            background: #fff;
            z-index: 1000;
            margin-top: 5px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

            &.visible {
                opacity: 1;
                visibility: visible;
            }
        }

        & .datepicker-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        & .month-year-selector {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        & .nav-button {
            background: #f0f0f0;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;

            &:hover {
                background: #e0e0e0;
            }
        }

        & .clear-button {
            background: #ff4444;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;

            &:hover {
                background: #ff0000;
            }
        }

        & .calendar {
            width: 100%;
            border-collapse: collapse;

            & th {
                padding: 8px;
                background: #f0f0f0;
                color: #333;
            }
        }

        & .calendar td {
            padding: 8px;
            text-align: center;
            cursor: pointer;
            border: 1px solid #eee;
            position: relative;

            &:hover {
                background: #f0f0f0;
            }
        }

        & .date {
          color: black;
        }

        & .current-date {
            background: #007bff;
            color: white !important;
            border-radius: 50%;
            position: relative;
        }

        & .selected-date {
            background: #e3f2fd;
            border: 2px solid #007bff;
        }

        .other-month {
            color: #ccc;
        }
    }
</style>
