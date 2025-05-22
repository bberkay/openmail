<script lang="ts">
    import { type Email, type Account } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import Unsubscribe from "./Others/Unsubscribe.svelte";
    import ViewSource from "./Others/ViewSource.svelte";
    import Print from "./Others/Print.svelte";
    import Spam from "./Others/Spam.svelte";

    interface Props {
        account: Account;
        email: Email
    }

    let {
        account,
        email
    } = $props();
</script>

<div class="tool">
    <Dropdown.Root>
        <Dropdown.Toggle>⋮</Dropdown.Toggle>
        <Dropdown.Content>
            <Spam {account} {email}>
                {local.spam[DEFAULT_LANGUAGE]}
            </Spam>
            <Print {account} {email}>
                {local.print[DEFAULT_LANGUAGE]}
            </Print>
            <ViewSource {account} {email}>
                {local.view_source[DEFAULT_LANGUAGE]}
            </ViewSource>
            <Unsubscribe {account} {email}>
                {local.unsubscribe[DEFAULT_LANGUAGE]}
            </Unsubscribe>
        </Dropdown.Content>
    </Dropdown.Root>
</div>
