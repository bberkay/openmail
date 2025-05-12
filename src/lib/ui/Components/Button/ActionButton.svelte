<script lang="ts">
    import { mount, unmount, type Snippet } from "svelte";
    import { combine } from "$lib/utils";
    import { Spinner } from "$lib/ui/Components/Loader";
    import * as Button from "$lib/ui/Components/Button";

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

    let {
	    class: additionalClass,
		...restAttributes
	} = $derived(attributes);

    const makeAnAction = async (e: Event): Promise<void> => {
        e.preventDefault();

        const eventTrigger = e.target as HTMLButtonElement;
        if (!eventTrigger)
            return;

        eventTrigger.disabled = true;
        const temp = eventTrigger.innerText;
        eventTrigger.innerText = "";
        const loader = mount(Spinner, { target: eventTrigger });

        await onclick(e);

        eventTrigger.disabled = false;
        eventTrigger.innerText = temp;
        unmount(loader);
    }
</script>

<Button.Basic
    type="button"
    onclick={makeAnAction}
    class={combine("btn", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</Button.Basic>
