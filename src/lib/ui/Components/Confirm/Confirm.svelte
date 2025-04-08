<script lang="ts">
    import { onMount } from "svelte";
    import { close, type Props } from "./index";
    import * as Button from "$lib/ui/Components/Button";

    let {
        content,
        onConfirmText,
        onConfirm,
        onCancelText,
        onCancel
    }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });

    const onCancelWrapper = async (e: Event): Promise<void> => {
        if (onCancel) await onCancel(e);
        close();
    };

    const onConfirmWrapper = async (e: Event): Promise<void> => {
        await onConfirm(e);
        close();
    };
</script>

<div class="modal confirm">
    {@html content}
    <Button.Action
        type="button"
        onclick={onCancelWrapper}
    >
        {onCancelText || "Cancel"}
    </Button.Action>
    <Button.Action
        type="button"
        onclick={onConfirmWrapper}
    >
        {onConfirmText}
    </Button.Action>
</div>

<style>
    .modal.confirm {
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
