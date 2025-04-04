<script lang="ts">
    import { type Mailbox } from "$lib/types";
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Mailbox/Toolbox/ToolboxRight.svelte";

    interface Props {
        emailSelection: "1:*" | string[];
        currentMailbox: Mailbox;
    }

    let {
        emailSelection = $bindable([]),
        currentMailbox
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft bind:emailSelection {currentMailbox} />
    <ToolboxRight {currentMailbox} />
</div>
