<script lang="ts">
	let { children } = $props();
</script>

<div id="layout-container">
    {@render children()}
</div>

<div id="modal-container"></div>
<div id="notification-container"></div>
