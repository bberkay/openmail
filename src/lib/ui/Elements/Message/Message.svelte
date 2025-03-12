<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";

    interface Props {
        content: string;
        onOkText?: string;
        onOk?: (e: Event) => void;
    }

    let {
        content,
        onOkText,
        onOk
    }: Props = $props();

    onMount(() => {
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    });

    const onOkWrapper = (e: Event) => {
        if (onOk) onOk(e);
        close();
    };
</script>

<div class="modal confirm">
    {@html content}
    <button type="button" onclick={onOkWrapper}>{onOkText || "Ok"}</button>
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
