<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import ToolboxLeft from "$lib/ui/Layout/Main/Content/Email/Toolbox/ToolboxLeft.svelte";
    import ToolboxRight from "$lib/ui/Layout/Main/Content/Email/Toolbox/ToolboxRight.svelte";

    interface Props {
        account: Account;
        email: Email;
        previouslyAtHome: boolean;
    }

    let {
        account,
        email,
        previouslyAtHome
    }: Props = $props();
</script>

<div class="toolbox">
    <ToolboxLeft {account} {email} {previouslyAtHome} />
    <ToolboxRight {account} {email} />
</div>
