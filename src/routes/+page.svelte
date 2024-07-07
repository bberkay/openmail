<script lang="ts">
	import Alert from "$lib/components/Alert.svelte";
	import Sidebar from "$lib/components/Sidebar.svelte";
	import Inbox from "$lib/components/Inbox.svelte";
	import Email from "$lib/components/Email.svelte";
	import Login from "$lib/components/Login.svelte";

	let is_logged_in = false;
</script>

<Alert message="This is a success message" type="success" />
{#if !is_logged_in}
	<Login />
{:else}
	<main class="container">
		<div class="sidebar-container">
			<Sidebar />
		</div>
		<div class="inbox-container">
			<Inbox />
		</div>
		<div class="email-container">
			<Email />		
		</div>
</main>
{/if}


<style>
	.container{
		max-height: 100vh;
		max-width: 100vw;
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