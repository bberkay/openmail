<script lang="ts">
    import { Tween } from 'svelte/motion';
    import { cubicOut } from "svelte/easing";
    import BasicInput from "./BasicInput.svelte";
    import BasicButton from '$lib/ui/Components/Button/BasicButton.svelte';
    import Icon from '$lib/ui/Components/Icon';

    interface Props {
        toggleButtonIconName?: string;
        [attribute: string]: unknown;
    }

    let {
        toggleButtonIconName,
        ...attributes
    }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;

    let isOpen = $state(false);
    let inputValue = $state("");

    const tween = new Tween(60, {
        duration: 300,
        easing: cubicOut,
    });

    const toggleInput = () => {
        isOpen = !isOpen;

        if (isOpen) {
            tween.set(300);
        } else {
            tween.set(60);
            inputValue = "";
        }
    }

    const closeInput = () => {
        if(isOpen) toggleInput();
    }
</script>

<svelte:window onkeydown={closeInput} />

<div class="expandable-container" style="width:{tween.current}px">
    {#if isOpen}
        <div class="input-container">
            <BasicInput
                type="text"
                bind:value={inputValue}
                autofocus
                {...restAttributes}
            />
            <BasicButton
                type="button"
                class="close-button"
                onclick={toggleInput}
            >
                <Icon name="close" />
            </BasicButton>
        </div>
    {:else}
        <BasicButton
            type="button"
            class="toggle-button"
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
            height: 40px;
            overflow: hidden;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;

            & .input-container {
                display: flex;
                width: 100%;
                height: 100%;
                align-items: center;
                background-color: white;
                border-radius: 20px;
            }

            & input {
                flex: 1;
                height: 100%;
                border: none;
                padding: 0 15px;
                font-size: 16px;
                outline: none;
                background: transparent;
            }

            & .toggle-button {
                width: 100%;
                height: 100%;
                border: none;
                background-color: #4285f4;
                color: white;
                cursor: pointer;
                border-radius: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                transition: background-color 0.2s;

                &:hover {
                    background-color: #3b78e7;
                }
            }

            & .close-button {
                width: 40px;
                height: 40px;
                border: none;
                background: none;
                cursor: pointer;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #666;

                &:hover {
                    color: #333;
                }
            }
        }
    }
</style>
