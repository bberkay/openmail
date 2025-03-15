<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Elements/Button";

    interface Props {
        content: string;
        onConfirmText: string;
        onConfirm: (e: Event) => void;
        onCancelText?: string;
        onCancel?: (e: Event) => void;
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

    const onCancelWrapper = (e: Event) => {
        if (onCancel) onCancel(e);
        close();
    };

    const onConfirmWrapper = (e: Event) => {
        onConfirm(e);
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
    .confirm {
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
