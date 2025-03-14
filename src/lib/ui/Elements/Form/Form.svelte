<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { Spinner } from "$lib/ui/Elements/Loader";
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

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<form
    class={combine("form", additionalClass)}
    onsubmit={makeAnApiRequest}
    {...restAttributes}
>
    {@render children()}
</form>

<style>
    :global {
        .form {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);
        }
    }
</style>
