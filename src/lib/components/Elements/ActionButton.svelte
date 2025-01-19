<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import Loader from "$lib/components/Elements/Loader.svelte";

    interface Props {
        id: string;
        operation: (eventTrigger: HTMLButtonElement) => Promise<void>,
        children: Snippet;
        [attribute: string]: unknown;
    }

    let {
        id,
        operation,
        children,
        ...attributes
    }: Props = $props();

    const makeAnApiRequest = async (e: Event): Promise<void> => {
        e.preventDefault();

        const eventTrigger = document.getElementById(id) as HTMLButtonElement;
        if (!eventTrigger)
            return;

        eventTrigger.disabled = true;
        const temp = eventTrigger.innerText;
        eventTrigger.innerText = "";
        const loader = mount(Loader, { target: eventTrigger });

        await operation(eventTrigger);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
    }
</script>

<button {...attributes} type="button" id={id} onclick={makeAnApiRequest}>
    {@render children()}
</button>

<style>

</style>
