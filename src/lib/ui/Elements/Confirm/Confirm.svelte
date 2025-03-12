<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";

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
    <button type="button" onclick={onCancelWrapper}>
        {onCancelText || "Cancel"}
    </button>
    <button type="button" onclick={onConfirmWrapper}>{onConfirmText}</button>
</div>

<style>
    .modal {
        background-color: #2e2e2e;
        border: 1px solid #5a5a5a;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 5px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 99999;
    }
</style>
