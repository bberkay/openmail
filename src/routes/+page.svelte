<script lang="ts">
    import { onMount } from "svelte";
    import { get } from "svelte/store";
    import Alert from "$lib/components/Alert.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Content from "$lib/components/Content.svelte";
    import Register from "$lib/components/Register.svelte";
    import type { OpenMailData, Email } from "$lib/types";
    import { Store } from "@tauri-apps/plugin-store";
    import {
        serverUrl,
        emails,
        totalEmailCount,
        currentFolder,
        folders,
        currentOffset,
        accounts,
    } from "$lib/stores";

    let isLoading: boolean = true;

    onMount(async () => {
        if (get(accounts).length === 0) getAccounts();
        else isLoading = false;
    });

    async function saveData() {
        const store = new Store("openmail_cache.bin");
        await store.set("cache", {
            accounts: get(accounts),
            emails: get(emails),
            totalEmailCount: get(totalEmailCount),
            currentFolder: get(currentFolder),
            folders: get(folders),
            currentOffset: get(currentOffset),
        });
    }

    async function getAccounts() {
        const response: OpenMailData = await fetch(
            `${get(serverUrl)}/get-email-accounts`,
        ).then((res) => res.json());
        if (Object.hasOwn(response, "data") && response.data) {
            accounts.set(response.data);
            saveData();
        }
        isLoading = false;
    }

    async function getEmails() {
        const response: OpenMailData = await fetch(
            `${get(serverUrl)}/fetch-emails`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    accounts: get(accounts).map((account) => account["email"]),
                }),
            },
        ).then((res) => res.json());
        if (response.success) {
            emails.set(response.data["emails"] as Email[]);
            currentFolder.set(response.data["folder"]);
            currentOffset.set(
                response.data["total"] < 10 ? response.data["total"] : 10,
            );
            totalEmailCount.set(response.data["total"]);
            saveData();
        }
    }

    async function getFolders() {
        const response: OpenMailData = await fetch(
            `${get(serverUrl)}/get-folders/${get(accounts)[0]["email"]}`, // FIXME: Temporary
        ).then((res) => res.json());
        if (response.success) {
            folders.set(response.data);
            saveData();
        }
    }
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if $emails.length > 0}
    <main class="container">
        <div class="sidebar-container">
            <Sidebar />
        </div>
        <div class="inbox-container">
            <Inbox />
        </div>
        <div class="email-container">
            <Content />
        </div>
    </main>
{:else if isLoading}
    <p>Loading</p>
{:else}
    <Register
        on:continueToInbox={async () => {
            await getEmails();
            await getFolders();
        }}
    />
{/if}

<style>
    .container {
        display: flex;
    }

    .sidebar-container {
        width: 25%;
    }

    .inbox-container {
        width: 35%;
    }

    .email-container {
        width: 40%;
    }
</style>
