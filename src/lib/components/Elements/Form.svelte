<script lang="ts">
    import { mount, unmount } from "svelte";
    import Loader from "$lib/components/Elements/Loader.svelte";
    import type { Snippet } from 'svelte';

    interface Props {
        children: Snippet;
        onsubmit: (form: HTMLFormElement) => Promise<void>
    }

    let { children, onsubmit }: Props = $props();

    const makeAnApiRequest = async (e: Event) => {
        e.preventDefault();

        const form = e.target as HTMLFormElement;
        const eventTrigger = form.querySelector(
            'button[type="submit"]'
        ) as HTMLButtonElement;

        if (!eventTrigger)
            return;

        eventTrigger.disabled = true;
        const temp = eventTrigger.innerText;
        eventTrigger.innerText = "";
        const loader = mount(Loader, { target: eventTrigger });

        await onsubmit(form);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
        form.reset();
    }
</script>

<form onsubmit={makeAnApiRequest}>
    {@render children()}
</form>
