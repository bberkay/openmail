<script lang="ts">
    import { Tween } from 'svelte/motion';
    import { cubicOut } from "svelte/easing";
    import BasicInput from "./BasicInput.svelte";
    import BasicButton from '$lib/ui/Components/Button/BasicButton.svelte';
    import Icon from '$lib/ui/Components/Icon';
    import InputGroup from './InputGroup.svelte';

    interface Props {
        direction?: "left" | "right";
        onClose?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        toggleButtonIconName?: string;
        [attribute: string]: unknown;
    }

    let {
        direction = "left",
        onClose,
        toggleButtonIconName,
        ...attributes
    }: Props = $props();

    let expandableContainer: HTMLElement;
    let isOpen = $state(false);
    let inputValue = $state("");

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    const tween = new Tween(20, {
        duration: 300,
        easing: cubicOut,
    });

    const toggleInput = async (e: Event) => {
        isOpen = !isOpen;

        if (isOpen) {
            tween.set(200);
        } else {
            tween.set(20);
            inputValue = "";
            if(onClose) await onClose(e);
        }
    }

    const handleClickOutside = (e: MouseEvent) => {
        setTimeout(() => {
          if (isOpen &&
              !expandableContainer.contains(document.activeElement)) {
            toggleInput(e);
          }
        }, 100);
    }
</script>


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
            <!--onblur={handleClickOutside}-->
            <BasicInput
                type="text"
                bind:value={inputValue}
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
        }
    }
</style>
