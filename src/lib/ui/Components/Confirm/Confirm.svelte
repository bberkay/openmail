<script lang="ts">
    import { onMount } from "svelte";
    import { close, type Props } from "./index";
    import * as Button from "$lib/ui/Components/Button";
    import { combine } from "$lib/utils";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    let {
        title,
        onConfirmText,
        onConfirm,
        details,
        onCancelText,
        onCancel,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

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

<div
    class={combine("modal confirm", additionalClass)}
    {...restAttributes}
>
    <h3>{title}</h3>
    {#if details}
        <p>{@html details}</p>
    {/if}
    <Button.Action
        type="button"
        onclick={onCancelWrapper}
    >
        {onCancelText || local.cancel[DEFAULT_LANGUAGE]}
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
