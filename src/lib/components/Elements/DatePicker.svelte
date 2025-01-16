<script lang="ts">
    import { onMount } from "svelte";
    import { range, getMonths, convertToIMAPDate } from "$lib/utils";

    interface Props {
        id: string;
    }

    let { id }: Props = $props();

    let currentDate = new Date();
    let currentYear = currentDate.getFullYear();
    let currentMonth = currentDate.getMonth();
    let displayedYear: number = $state(currentYear);
    let displayedMonth: number = $state(currentMonth);
    let selectedDate: Date | "" = "";

    let datePickerShown: boolean = $state(false);
    let datePickerWrapper: HTMLDivElement;
    let dateInput: HTMLInputElement;
    let calendarBody: HTMLElement;

    onMount(() => {
        datePickerWrapper = document.getElementById(id) as HTMLDivElement;
        dateInput = datePickerWrapper.querySelector(
            ".date-input",
        ) as HTMLInputElement;
        calendarBody = datePickerWrapper.querySelector("#calendar-body")!;

        document.addEventListener("click", (e) => {
            if (
                !datePickerWrapper.contains(e.target as HTMLElement) &&
                e.target !== dateInput
            ) {
                datePickerShown = false;
            }
        });

        renderCalendar();
    });

    const selectMonth = (e: Event) => {
        if (!e.target) return;

        const target = e.target as HTMLInputElement;
        displayedMonth = parseInt(target.value);
        renderCalendar();
    };

    const selectYear = (e: Event) => {
        if (!e.target) return;

        const target = e.target as HTMLInputElement;
        displayedYear = parseInt(target.value);
    };

    const goPrevMonth = () => {
        displayedMonth--;
        if (displayedMonth < 0) {
            displayedMonth = 11;
            displayedYear--;
        }
    };

    const goNextMonth = () => {
        displayedMonth++;
        if (displayedMonth > 11) {
            displayedMonth = 0;
            displayedYear++;
        }
    };

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
                if (i === 0 && j < startingDay) {
                    const prevMonthLastDay = new Date(
                        displayedYear,
                        displayedMonth,
                        0,
                    ).getDate();
                    const prevMonthDay =
                        prevMonthLastDay - (startingDay - j - 1);
                    row += `<td class="other-month">${prevMonthDay}</td>`;
                } else if (date > totalDays) {
                    row += `<td class="other-month">${date - totalDays}</td>`;
                    date++;
                } else if (date <= totalDays) {
                    const isCurrentDate =
                        date === currentDate.getDate() &&
                        displayedMonth === currentDate.getMonth() &&
                        displayedYear === currentDate.getFullYear();

                    const isSelectedDate =
                        selectedDate &&
                        date === selectedDate.getDate() &&
                        displayedMonth === selectedDate.getMonth() &&
                        displayedYear === selectedDate.getFullYear();

                    const classes = [];
                    if (isCurrentDate) classes.push("current-date");
                    if (isSelectedDate) classes.push("selected-date");

                    row += `<td class="${classes.join(" ")}"
                                  data-date="${date}">${date}</td>`;
                    date++;
                }
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
                    selectedDate = new Date(
                        displayedYear,
                        displayedMonth,
                        parseInt(cell.dataset.date!),
                    );
                    datePickerShown = false;
                    renderCalendar();
                });
            });
    }
</script>

<div class="date-input-wrapper {!datePickerShown ? 'hidden' : ''}" {id}>
    <input
        type="text"
        class="date-input"
        readonly
        placeholder="Select date"
        value={() => {
            convertToIMAPDate(selectedDate);
        }}
        onclick={() => {
            datePickerShown = true;
        }}
    />
    <div class="datepicker-container">
        <div class="datepicker-header">
            <div class="month-year-selector">
                <button class="nav-button" id="prevMonth" onclick={goPrevMonth}
                    >←</button
                >
                <select
                    id="monthSelect"
                    value={displayedMonth}
                    onchange={selectMonth}
                >
                    {#each getMonths() as month, index}
                        <option value={index}>{month}</option>
                    {/each}
                </select>
                <select
                    id="yearSelect"
                    value={displayedYear}
                    onchange={selectYear}
                >
                    {#each range(currentYear - 10, currentYear + 10, 1) as year}
                        <option value={year}>{year}</option>
                    {/each}
                </select>
                <button class="nav-button" id="nextMonth" onclick={goNextMonth}
                    >→</button
                >
            </div>
        </div>
        <table class="calendar">
            <thead>
                <tr>
                    <th>Sun</th>
                    <th>Mon</th>
                    <th>Tue</th>
                    <th>Wed</th>
                    <th>Thu</th>
                    <th>Fri</th>
                    <th>Sat</th>
                </tr>
            </thead>
            <tbody id="calendarBody"></tbody>
        </table>
    </div>
</div>

<style>
    .date-input-wrapper :global {
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
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            width: 300px;
            font-family: Arial, sans-serif;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            background: #fff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            margin-top: 5px;
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

        & select {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 3px;
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
