<script lang="ts">
    import { onMount } from "svelte";
    import { get } from "svelte/store";
    import Alert from "$lib/components/Alert.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import Inbox from "$lib/components/Inbox.svelte";
    import Content from "$lib/components/Content.svelte";
    import Register from "$lib/components/Register.svelte";
    import type { Response } from "$lib/types";
    import { Store } from "@tauri-apps/plugin-store";
    import {
        serverUrl,
        emails,
        currentFolder,
        folders,
        currentOffset,
        accounts,
    } from "$lib/stores";

    let isLoading: boolean = true;

    onMount(async () => {
        serverUrl.subscribe(url => {
          if(url.length > 0){
            if (get(accounts).length === 0) getAccounts();
            else isLoading = false;
          }
        });
    });

    async function saveData() {
        const store = new Store("openmail_cache.bin");
        await store.set("cache", {
            accounts: get(accounts),
            emails: get(emails),
            currentFolder: get(currentFolder),
            folders: get(folders),
            currentOffset: get(currentOffset),
        });
    }

    async function getAccounts() {
        const response: Response = await fetch(
            `${get(serverUrl)}/get-email-accounts`,
        ).then((res) => res.json());
        if (Object.hasOwn(response, "data") && response.data) {
            accounts.set(response.data);
            saveData();
        }
        isLoading = false;
    }

    async function getEmailsOfAllAccounts() {
        const response: Response = await fetch(
            `${get(serverUrl)}/get-emails/${get(accounts)
                .map((account) => account["email"])
                .join(",")}`
        ).then((res) => res.json());
        if (response.success) {
            emails.set(
                response.data.map((item: { email: string; data: object }) => ({
                    email: item.email,
                    ...item.data
                }))
            );
            currentFolder.set("Inbox");
            currentOffset.set(
                response.data["total"] < 10 ? response.data["total"] : 10,
            );
            saveData();
        }
    }

    async function getFoldersOfAllAccounts() {
        const response: Response = await fetch(
            `${get(serverUrl)}/get-folders/${get(accounts)
                .map((account) => account["email"])
                .join(",")}`
        ).then((res) => res.json());
        if (response.success) {
            folders.set(
              response.data.map((item: { email: string; data: any }) => ({
                  email: item.email,
                  folders: item.data,
              })),
            );
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
            await getEmailsOfAllAccounts();
            await getFoldersOfAllAccounts();
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
