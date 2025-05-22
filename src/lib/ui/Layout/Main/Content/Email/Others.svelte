<script lang="ts">
    import { DEFAULT_LANGUAGE } from "$lib/constants";
    import { local } from "$lib/locales";
    import * as Popover from "$lib/ui/Components/Popover";

    interface Props {
        toggleText: string;
        receivers: string;
        cc?: string;
        bcc?: string;
    }

    let {
        toggleText,
        receivers,
        cc,
        bcc
    }: Props = $props();
</script>

<Popover.Root>
    <Popover.Toggle>
        {toggleText}
    </Popover.Toggle>
    <Popover.Content>
        <span>
            <b>{local.receiver_s[DEFAULT_LANGUAGE]}:</b>
            <small>{receivers}</small>
        </span>
        {#if cc}
            <span>
                <b>{local.cc[DEFAULT_LANGUAGE]}:</b>
                <small>{cc}</small>
            </span>
        {/if}
        {#if bcc}
            <span>
                <b>{local.bcc[DEFAULT_LANGUAGE]}:</b>
                <small>{bcc}</small>
            </span>
        {/if}
    </Popover.Content>
</Popover.Root>
