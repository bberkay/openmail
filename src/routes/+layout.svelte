<script lang="ts">
    import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
        document.body.addEventListener("click", (e: MouseEvent) => {
            const target = e.target as HTMLInputElement;
            const dropdowns = document.querySelectorAll(".dropdown");
            if (!dropdowns.length)
                return;

            if (!target.closest('.dropdown, .dropdown-toggle') || (target.closest('.dropdown') && !target.closest('select'))) {
                dropdowns.forEach(dropdown => dropdown.remove());
            }
        });
	});
</script>

<main>
    {@render children()}
</main>

<div id="modal-container"></div>
