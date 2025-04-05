<script lang="ts">
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxRight.svelte";

    interface Props {
        emailSelection: "1:*" | string[];
    }

    let {
        emailSelection = $bindable([]),
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft bind:emailSelection />
    <ToolboxRight />
</div>
