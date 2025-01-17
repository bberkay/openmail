<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Loader.svelte";

    interface Props {
        id: string;
        operation: (eventTrigger: HTMLButtonElement) => Promise<void>,
        inner: string;
        classes?: string | undefined;
        [attribute: string]: unknown;
    }

    let {
        id,
        operation,
        inner,
        classes = "",
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

<button id={id} class={classes} {...attributes} onclick={makeAnApiRequest}>
    {@html inner}
</button>

<style>

</style>
