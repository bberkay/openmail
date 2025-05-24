<script lang="ts">
    import { onMount } from "svelte";
    import { close, type Props } from "./index";
    import { combine } from "$lib/utils";
    import * as Button from "$lib/ui/Components/Button";
    import { local } from "$lib/locales";
    import { DEFAULT_LANGUAGE } from "$lib/constants";

    let {
        title,
        details,
        onCloseText,
        onClose,
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

    const onCloseWrapper = async (e: Event) => {
        if (onClose) await onClose(e);
        close();
    };
</script>

<div
    class={combine("modal message", additionalClass)}
    {...restAttributes}
>
    <h3>{title}</h3>
    {#if details}
        <p>{@html details}</p>
    {/if}
    <Button.Action
        type="button"
        class="btn-outline"
        onclick={onCloseWrapper}
    >
        {onCloseText || local.close[DEFAULT_LANGUAGE]}
    </Button.Action>
</div>

<style>
    .modal.message{
        opacity: 1; /* temporary for prevent empty ruleset warning */
    }
</style>
