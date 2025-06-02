<script lang="ts">
    import type { Snippet } from "svelte";
    import { type Email, type Account } from "$lib/types";
    import * as Dropdown from "$lib/ui/Components/Dropdown";
    import { show as showMessage } from "$lib/ui/Components/Message";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { getNotImplementedTemplate } from "$lib/templates";

    interface Props {
        children: Snippet,
        account: Account;
        email: Email;
    }

    let {
        children,
        account,
        email
    }: Props = $props();
</script>

<Dropdown.Item
    onclick={() => {
        showMessage({
            title: getNotImplementedTemplate(
                local.spam[DEFAULT_LANGUAGE],
            ),
        });
    }}
>
    {@render children()}
</Dropdown.Item>
