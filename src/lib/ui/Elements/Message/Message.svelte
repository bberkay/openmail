<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Elements/Button";

    interface Props {
        content: string;
        onCloseText?: string;
        onClose?: (((e: Event) => void) | ((e: Event) => Promise<void>));
    }

    let {
        content,
        onCloseText,
        onClose
    }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });

    const onOkWrapper = async (e: Event) => {
        if (onClose) await onClose(e);
        close();
    };
</script>

<div class="modal message">
    {@html content}
    <Button.Basic
        type="button"
        onclick={onOkWrapper}
    >
        {onCloseText || "Close"}
    </Button.Basic>
</div>

<style>
    .modal.message{
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
