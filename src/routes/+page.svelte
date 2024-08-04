<script lang="ts">
	import Alert from "$lib/components/Alert.svelte";
	import Sidebar from "$lib/components/Sidebar.svelte";
	import Inbox from "$lib/components/Inbox.svelte";
	import Content from "$lib/components/Content.svelte";
	import Register from "$lib/components/Register.svelte";
	import { serverUrl, emails, totalEmailCount, currentFolder, folders, currentOffset, accounts } from "$lib/stores";
    import type { OpenMailData, Email } from "$lib/types";
    import { invoke } from '@tauri-apps/api/core';
    import { onMount } from "svelte";
    import { get } from "svelte/store";

	let isLoading: boolean = true;
	let continueToInbox: boolean = false;
	onMount(async () => {
	    await setServerUrl();
        await getAccounts();
    });

	async function setServerUrl(){
	    await invoke('get_server_url').then(url => {
			serverUrl.set(url ? url as string : "http://127.0.0.1:8000");
        });
	}

	async function getAccounts(){
        const response: OpenMailData = await fetch(`${get(serverUrl)}/get-email-accounts`).then(res => res.json());
        if(Object.hasOwn(response, "data") && response.data)
            accounts.set(response.data);
        isLoading = false;
	}

	async function getEmails(){
	    continueToInbox = true;
		console.log("Getting emails...");
		/*const response: OpenMailData = await fetch(`${get(serverUrl)}/get-emails`).then(res => res.json());
        if(response.success){
            emails.set(response.data["emails"] as Email[]);
            currentFolder.set(response.data["folder"]);
            currentOffset.set(response.data["total"] < 10 ? response.data["total"] : 10);
            totalEmailCount.set(response.data["total"]);
        }*/
	}

	async function getFolders(){
		const response: OpenMailData = await fetch(`${get(serverUrl)}/get-folders`).then(res => res.json());
		if(response.success)
		    folders.set(response.data);
	}
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if isLoading}
    <p>Loading</p>
{:else}
    {#if !continueToInbox}
    	<Register on:continueToInbox={getEmails} />
    {:else}
    	<main class="container">
    		<div class="sidebar-container">
    			<Sidebar />
    		</div>
    		<div class="inbox-container">
    			<Inbox/>
    		</div>
    		<div class="email-container">
    			<Content />
    		</div>
    	</main>
     {/if}
{/if}

<style>
	.container{
		display: flex;
	}

	.sidebar-container{
		width: 25%;
	}

	.inbox-container{
		width: 35%;
	}

	.email-container{
		width: 40%;
	}
</style>
