<script lang="ts">
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Inbox/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Inbox/Toolbox/ToolboxRight.svelte";

    interface Props {
        emailSelection: string[];
    }

    let {
        emailSelection = $bindable([])
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft bind:emailSelection />
    <ToolboxRight />
</div>
