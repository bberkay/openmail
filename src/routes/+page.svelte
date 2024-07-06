<script lang="ts">
	import Alert from "$lib/Alert.svelte";
	import { invoke } from "@tauri-apps/api/core";
	
	let emails = "";
	async function getEmails() {
		emails = "Loading...";
		const email = document.querySelector("input")!.value;
		emails = await invoke("get_emails", { email });
	}
</script>

<div class="container">
	<Alert message="This is a success message" type="success" />
	<input type="text" placeholder="Enter email" />
	<button type="submit" on:click={getEmails}>Get Emails</button>
	<p>{emails}</p>
</div>

<style>
	.container{
		max-height: 100vh;
		max-width: 100vw;
	}
</style>