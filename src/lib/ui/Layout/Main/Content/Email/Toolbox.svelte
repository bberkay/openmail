<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Email/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Email/Toolbox/ToolboxRight.svelte";

    interface Props {
        account: Account;
        email: Email;
        currentOffset: number;
    }

    let {
        account,
        email = $bindable(),
        currentOffset = $bindable()
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft {account} {email} {currentOffset} />
    <ToolboxRight {account} bind:email bind:currentOffset />
</div>
