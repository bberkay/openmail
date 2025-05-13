<script lang="ts">
    import { Tween } from 'svelte/motion';
    import { cubicOut } from "svelte/easing";
    import BasicInput from "./BasicInput.svelte";
    import BasicButton from '$lib/ui/Components/Button/BasicButton.svelte';
    import Icon from '$lib/ui/Components/Icon';
    import InputGroup from './InputGroup.svelte';

    const DEFAULT_COLLAPSED_WIDTH = 20;
    const DEFAULT_EXPANDED_WIDTH = 200;
    const DEFAULT_EXPAND_DURATION = 300;

    interface Props {
        direction?: "left" | "right";
        onClose?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        toggleButtonIconName?: string;
        collapsedWidth?: number;
        expandedWidth?: number;
        expandDuration?: number;
        collapseWhenClickedOutside?: boolean,
        [attribute: string]: unknown;
    }

    let {
        direction = "left",
        onClose,
        toggleButtonIconName,
        collapsedWidth = DEFAULT_COLLAPSED_WIDTH,
        expandedWidth = DEFAULT_EXPANDED_WIDTH,
        expandDuration = DEFAULT_EXPAND_DURATION,
        collapseWhenClickedOutside = false,
        ...attributes
    }: Props = $props();

    let expandableContainer: HTMLElement;
    let isOpen = $state(false);
    let inputValue = $state("");

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    const tween = new Tween(collapsedWidth, {
        duration: expandDuration,
        easing: cubicOut,
    });

    const toggleInput = async (e: Event) => {
        isOpen = !isOpen;

        if (isOpen) {
            tween.set(expandedWidth);
        } else {
            tween.set(collapsedWidth);
            inputValue = "";
            if(onClose) await onClose(e);
        }
    }

    const handleClickOutside = (e: MouseEvent) => {
        if (!collapseWhenClickedOutside)
            return;

        setTimeout(() => {
          if (isOpen &&
              !expandableContainer.contains(document.activeElement)) {
            toggleInput(e);
          }
        }, 100);
    }
</script>

<svelte:window onclick={handleClickOutside} />

<div
    bind:this={expandableContainer}
    class="expandable-container"
    style="
        width:{tween.current}px;
        transform-origin:{direction};
        {direction == "left" ? "margin-left:auto" : ""}
    "
>
    {#if isOpen}
        <InputGroup>
            <BasicInput
                type="text"
                bind:value={inputValue}
                onblur={handleClickOutside}
                autofocus
                {...restAttributes}
            />
            <BasicButton
                type="button"
                onclick={toggleInput}
            >
                <Icon name="close" />
            </BasicButton>
        </InputGroup>
    {:else}
        <BasicButton
            type="button"
            class="btn-inline"
            onclick={toggleInput}
        >
            <Icon name={toggleButtonIconName || "search"} />
        </BasicButton>
    {/if}
</div>

<style>
    :global {
        .expandable-container {
            position: relative;
            display: flex;
            height: calc(var(--font-size-2xl) + 10px);
            align-items: center;

            & .input-group {
                width: 100%;
            }
        }
    }
</style>
