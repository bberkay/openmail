<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Toolbox from "./Email/Toolbox.svelte";
    import Content from "./Email/Content.svelte";

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

<Toolbox {account} {email} {previouslyAtHome} />
<Content {account} {email} />
