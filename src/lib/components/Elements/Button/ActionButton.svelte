<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import Loader from "$lib/components/Elements/Loader.svelte";

    interface Props {
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        onclick,
        children,
        ...attributes
    }: Props = $props();

    const makeAnApiRequest = async (e: Event): Promise<void> => {
        e.preventDefault();

        const eventTrigger = e.target as HTMLButtonElement;
        if (!eventTrigger)
            return;

        eventTrigger.disabled = true;
        const temp = eventTrigger.innerText;
        eventTrigger.innerText = "";
        const loader = mount(Loader, { target: eventTrigger });

        await onclick(e);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
    }
</script>

<button {...attributes} type="button" onclick={makeAnApiRequest}>
    {@render children()}
</button>

<style>

</style>
