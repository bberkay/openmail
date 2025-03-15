<script lang="ts">
    import { onMount } from "svelte";
    import { close } from "./index";
    import * as Button from "$lib/ui/Elements/Button";

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

<div class="modal message">
    {@html content}
    <Button.Basic
        type="button"
        onclick={onOkWrapper}
    >
        {onOkText || "Ok"}
    </Button.Basic>
</div>

<style>
    .modal.message{
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
