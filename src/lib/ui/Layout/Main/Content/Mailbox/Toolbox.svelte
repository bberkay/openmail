<script lang="ts">
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxRight.svelte";

    interface Props {
        emailSelection: "1:*" | string[];
        currentOffset: number;
    }

    let {
        emailSelection = $bindable([]),
        currentOffset = $bindable()
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft bind:emailSelection {currentOffset} />
    <ToolboxRight bind:currentOffset />
</div>
