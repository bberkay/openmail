<script lang="ts">
    import InboxItem from "./Inbox/InboxItem.svelte";
    import {
        emails,
        currentFolder,
        currentAccounts,
        currentOffset,
        serverUrl,
    } from "$lib/stores";
    import { get } from "svelte/store";
    import { onMount } from "svelte";
    import type { Response } from "$lib/types";

    let prevButton: HTMLButtonElement;
    let nextButton: HTMLButtonElement;
    let totalEmailCount = get(emails).reduce(
        (acc, account) => get(currentAccounts).find((a) => a.email == account.email) ? acc + account.total : acc,
        0,
    );
    onMount(() => {
        prevButton = document.getElementById(
            "prev-button",
        ) as HTMLButtonElement;
        nextButton = document.getElementById(
            "next-button",
        ) as HTMLButtonElement;

        currentOffset.subscribe(async (value) => {
            if (value < 10) return;

            /**
             * If user moves email to another folder, the offset will not be a multiple of 10.
             * In this case, we need to fetch the emails from the previous page to complete the page.
             * For example, if the offset is 13, we need to fetch the emails from 10 to 20.
             * This is not a good solution but it is enough for now.
             */
            const complete_to_ten = $currentOffset - ($currentOffset % 10);
            if (complete_to_ten != $currentOffset) {
                let response: Response = await fetch(
                    `${get(serverUrl)}/get-emails/${getCurrentAccountsAsString()}?folder=${encodeURIComponent(get(currentFolder))}&offset=${complete_to_ten.toString()}&search=${getSearchMenuValue()}`,
                ).then((response) => response.json());
                if (response.success) {
                  currentOffset.update((value) => 10 + complete_to_ten);
                  emails.set(
                      response.data.map((item: { email: string; data: object }) => ({
                          email: item.email,
                          ...item.data
                      }))
                  );
                }
            }
        });
    });

    function getSearchMenuValue() {
        const search = (document.getElementById("search") as HTMLInputElement)
            .value;
        return search.trim() == "" ? "" : search;
    }

    function getCurrentAccountsAsString() {
        return get(currentAccounts).map((account) => account.email).join(", ");
    }

    async function getPreviousEmails() {
        if (get(currentOffset) <= 10) return;

        prevButton.disabled = true;
        let response: Response = await fetch(
            `${get(serverUrl)}/get-emails/${getCurrentAccountsAsString()}?folder=${encodeURIComponent(get(currentFolder))}&offset=${get(currentOffset) - 20}&search=${getSearchMenuValue()}`,
        ).then((response) => response.json());
        if (response.success) {
            currentOffset.update((value) => value - 10);
            emails.set(
                response.data.map((item: { email: string; data: object }) => ({
                    email: item.email,
                    ...item.data
                }))
            );
        }
        prevButton.disabled = false;
    }

    async function getNextEmails() {
        if (get(currentOffset) >= totalEmailCount) return;

        nextButton.disabled = true;
        let response: Response = await fetch(
            `${get(serverUrl)}/get-emails/${getCurrentAccountsAsString()}?folder=${encodeURIComponent(get(currentFolder))}&offset=${get(currentOffset)}&search=${getSearchMenuValue()}`,
        ).then((response) => response.json());
        if (response.success) {
            currentOffset.update((value) => value + 10);
            emails.set(
                response.data.map((item: { email: string; data: object }) => ({
                    email: item.email,
                    ...item.data
                }))
            );
        }
        nextButton.disabled = false;
    }
</script>

<section class="card">
    <div class="inbox-header">
        <h2>{$currentFolder == "inbox" ? "Inbox" : $currentFolder}</h2>
        <hr />
        <div class="inbox-pagination">
            <button
                id="prev-button"
                on:click={getPreviousEmails}
                disabled={$currentOffset <= 10}>Previous</button>
            <small>{Math.max(1, $currentOffset - 9)} - {$currentOffset} of {totalEmailCount}</small>
            <button
                id="next-button"
                on:click={getNextEmails}
                disabled={$currentOffset >= totalEmailCount}>Next</button>
        </div>
        <hr />
    </div>
    <div class="inbox-content">
      {#each $emails as account}
        {#if get(currentAccounts).find((a) => a.email == account.email)}
          {#each account.emails as email}
            <InboxItem owner={account.email} email={email} />
          {/each}
        {/if}
      {/each}
    </div>
</section>

<style>
    .inbox-pagination {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .inbox-content {
        & h3 {
            margin: 0;
        }

        & .inbox-item:first-child {
            padding-top: 0.5rem;
        }

        & .inbox-item:last-child {
            border-bottom: none;
        }
    }
</style>
