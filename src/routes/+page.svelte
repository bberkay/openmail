<script lang="ts">
	import Alert from "$lib/components/Alert.svelte";
	import GetEmailsForm from "$lib/components/SendEmailForm.svelte";
	import SendEmailForm from "$lib/components/GetEmailsForm.svelte";
	import { invoke } from "@tauri-apps/api/core";
	
	let emails = "";
	async function getEmails() {
		emails = "Loading...";
		const email = document.querySelector("input")!.value;
		emails = await invoke("get_emails", { email });
	}
</script>

<Alert message="This is a success message" type="success" />
<main class="container">
	<div>
		<GetEmailsForm />
		<SendEmailForm />
	</div>
</main>

<style>
	.container{
		max-height: 100vh;
		max-width: 100vw;
		display: flex;
	}
</style>