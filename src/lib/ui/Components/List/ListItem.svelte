<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { Spinner } from "$lib/ui/Components/Loader";

    interface Props {
        children: Snippet;
        onclick?: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        type?: "disabled" | "active";
        [attribute: string]: unknown;
    }

    let {
        children,
        onclick,
        type,
        ...attributes
    }: Props = $props();

    const onClickWrapper = async (e: Event) => {
        e.preventDefault();

        const eventTrigger = e.target as HTMLButtonElement;
        if (!eventTrigger)
            return;

        eventTrigger.disabled = true;
        const temp = eventTrigger.innerText;
        eventTrigger.innerText = "";
        const loader = mount(Spinner, { target: eventTrigger });

        if(onclick && type !== "disabled") await onclick(e);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
    }
</script>

<li
    class="list-item {type} {onclick ? "clickable": ""}"
    onclick={onClickWrapper}
    {...attributes}
>
    {@render children()}
</li>

<style>
    :global {
        .list-container {
            .list-item {
                position: relative;
                display: block;
                padding: var(--spacing-sm);
                background-color: var(--color-bg-primary);
                border-bottom: 1px solid var(--color-border);
                text-decoration: none;
                color: var(--color-text-primary);
                transition: all var(--transition-fast) var(--ease-default);

                &:first-child {
                    border-top-left-radius: var(--radius-sm);
                    border-top-right-radius: var(--radius-sm);
                }

                &:hover {
                    background-color: var(--color-hover);
                    border-color: var(--color-text-primary);
                }

                &.clickable:active{
                    background-color: var(--color-border);
                }

                &.clickable {
                    cursor: pointer;
                }

                &.active {
                    background-color: var(--color-hover);
                    border-color: var(--color-text-primary);
                }
            }
        }
    }
</style>
