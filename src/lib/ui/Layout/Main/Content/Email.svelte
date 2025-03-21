<script lang="ts">
    import { type Account, type Email } from "$lib/types";
    import Toolbox from "./Email/Toolbox.svelte";
    import Content from "./Email/Content.svelte";

    interface Props {
        account: Account;
        email: Email;
    }

    let {
        account,
        email
    }: Props = $props();
</script>

<Toolbox {account} {email} />
<Content {account} {email} />
