<script lang="ts">
    import * as Popover from "$lib/ui/Components/Popover";

    interface Props {
        toggleText: string;
        receivers: string;
        cc?: string;
        bcc?: string;
    }

    let { toggleText, receivers, cc, bcc }: Props = $props();
</script>

<Popover.Root>
    <Popover.Toggle>
        {toggleText}
    </Popover.Toggle>
    <Popover.Content>
        <span>
            <b>Receivers:</b>
            <small>{receivers}</small>
        </span>
        {#if cc}
            <span>
                <b>Cc:</b>
                <small>{cc}</small>
            </span>
        {/if}
        {#if bcc}
            <span>
                <b>Bcc:</b>
                <small>{bcc}</small>
            </span>
        {/if}
    </Popover.Content>
</Popover.Root>

<style>
</style>
