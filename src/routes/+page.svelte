<script lang="ts">
	import Alert from "$lib/components/Alert.svelte";
	import Sidebar from "$lib/components/Sidebar.svelte";
	import Inbox from "$lib/components/Inbox.svelte";
	import Content from "$lib/components/Content.svelte";
	import Login from "$lib/components/Login.svelte";
	import { emails, totalEmailCount, currentFolder, folders, currentOffset, user } from "$lib/stores";
    import type { OpenMailData, Email } from "$lib/types";

	let is_logged_in: boolean = false;

	async function getAccounts(){
        const response: OpenMailData = await fetch('http://127.0.0.1:8000/get-accounts').then(res => res.json());
        if(Object.hasOwn(response, "data")){
            is_logged_in = true;
            /*user.set(response.data["user"]);
            emails.set(response.data["emails"]);
            totalEmailCount.set(response.data["total"]);
            currentFolder.set(response.data["folder"]);
            currentOffset.set(response.data["emails"].length);*/
        }
	}

	async function handleLoginDispatch(event: CustomEvent){
		is_logged_in = event.detail.success;
		if(is_logged_in){
		    user.set(event.detail.data);
			getEmails();
			//getFolders();
		}
	}

	async function getEmails(){
		const response: OpenMailData = await fetch('http://127.0.0.1:8000/get-emails').then(res => res.json());
        if(response.success){
            emails.set(response.data["emails"] as Email[]);
            currentFolder.set(response.data["folder"]);
            currentOffset.set(response.data["total"] < 10 ? response.data["total"] : 10);
            totalEmailCount.set(response.data["total"]);
        }
	}

	async function getFolders(){
		const response: OpenMailData = await fetch('http://127.0.0.1:8000/get-folders').then(res => res.json());
		if(response.success)
		    folders.set(response.data);
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
			<Content />
		</div>
	</main>
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
