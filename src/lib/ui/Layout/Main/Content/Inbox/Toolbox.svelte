<script lang="ts">
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Inbox/Toolbox/ToolboxLeft.svelte";

    interface Props {
        emailSelection: string[];
    }

    let {
        emailSelection = $bindable([])
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft bind:emailSelection />
</div>
