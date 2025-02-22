<script lang="ts">
    import * as Modal from "$lib/ui/Elements/Modal";
    import Layout from "$lib/ui/Layout/Layout.svelte";
    import Variables from "$lib/ui/Layout/Developer/Variables.svelte";

	let { children } = $props();

	const handleShortcuts = (e: KeyboardEvent) => {
        if (e.ctrlKey && e.code === 'Space') {
            e.preventDefault();
            Modal.show(Variables);
        }
	}
</script>

<svelte:window onkeydown={handleShortcuts} />

<Layout>
    {@render children()}
</Layout>

<div id="modal-container"></div>
<div id="notification-container"></div>
