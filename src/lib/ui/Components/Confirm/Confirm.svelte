<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        content: string;
        onConfirmText: string;
        onConfirm: (((e: Event) => void) | ((e: Event) => Promise<void>));
        onCancelText?: string;
        onCancel?: (((e: Event) => void) | ((e: Event) => Promise<void>));
    }

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
    <Button.Basic
        type="button"
        onclick={onCancelWrapper}
    >
        {onCancelText || "Cancel"}
    </Button.Basic>
    <Button.Basic
        type="button"
        onclick={onConfirmWrapper}
    >
        {onConfirmText}
    </Button.Basic>
</div>

<style>
    .modal.confirm {
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
