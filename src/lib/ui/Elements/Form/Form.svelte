<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { Spinner } from "$lib/ui/Elements/Loader";

    interface Props {
        children: Snippet;
        onsubmit: (e: Event) => Promise<void>
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
        const loader = mount(Spinner, { target: eventTrigger });

        await onsubmit(e);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
        form.reset();
    }
</script>

<form onsubmit={makeAnApiRequest}>
    {@render children()}
</form>
