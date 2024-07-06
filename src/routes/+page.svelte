<script lang="ts">
	import { invoke } from "@tauri-apps/api/core";
	
	let emails = "";
	async function getEmails() {
		emails = "Loading...";
		const email = document.querySelector("input")!.value;
		emails = await invoke("get_emails", { email });
	}
</script>

<div class="container">
	<h1>Welcome to Tauri!</h1>
	<input type="text" placeholder="Enter email" />
	<button type="submit" on:click={getEmails}>Get Emails</button>
	<p>{emails}</p>
</div>
