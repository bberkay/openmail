<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { Spinner } from "$lib/ui/Components/Loader";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet;
        onsubmit: (e: Event) => Promise<void>
        [attribute: string]: unknown;
    }

    let {
        children,
        onsubmit,
        ...attributes
    }: Props = $props();

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

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

<form
    onsubmit={makeAnApiRequest}
    class={combine("form", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</form>

<style>
    :global {
        .form {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-2xs);
        }
    }
</style>
