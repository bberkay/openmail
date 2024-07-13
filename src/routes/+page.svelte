<script lang="ts">
	import Alert from "$lib/components/Alert.svelte";
	import Sidebar from "$lib/components/Sidebar.svelte";
	import Inbox from "$lib/components/Inbox.svelte";
	import Email from "$lib/components/Email.svelte";
	import Login from "$lib/components/Login.svelte";
	import { emails, totalEmailCount, currentFolder, folders } from "$lib/stores";
	import { invoke } from "@tauri-apps/api/core";
    import type { OpenMailData, OpenMailDataString } from "$lib/types";

	let is_logged_in: boolean = false;

	async function handleLoginDispatch(event: CustomEvent){
		is_logged_in = event.detail.success;
		if(is_logged_in){
			getEmails(event);
			getFolders();
		}
	}

	async function getEmails(event: CustomEvent){
		// TODO: Implement this
		if(event.detail.success){
			emails.set(event.detail.data["emails"]);
			totalEmailCount.set(event.detail.data["total"]);
			currentFolder.set(event.detail.data["folder"]);
		}
	}

	async function getFolders(){
		let response: OpenMailDataString = await invoke('get_folders', {});
		let parsedResponse: OpenMailData = JSON.parse(response);
		if(parsedResponse.success)
			folders.set(parsedResponse.data);
	}
</script>

<!--<Alert message="This is a success message" type="success" />-->
{#if !is_logged_in}
	<Login on:login={handleLoginDispatch} />
{:else}
	<main class="container">
		<div class="sidebar-container">
			<Sidebar />
		</div>
		<div class="inbox-container">
			<Inbox/>
		</div>
		<div class="email-container">
			<Email />		
		</div>
	</main>
{/if}

<footer></footer>

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