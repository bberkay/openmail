<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Components/Button";

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

    const onCloseWrapper = async (e: Event) => {
        if (onClose) await onClose(e);
        close();
    };
</script>

<div class="modal message">
    {@html content}
    <Button.Action
        type="button"
        onclick={onCloseWrapper}
    >
        {onCloseText || "Close"}
    </Button.Action>
</div>

<style>
    .modal.message{
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
