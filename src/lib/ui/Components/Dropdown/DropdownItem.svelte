<script lang="ts">
    import type { Snippet } from "svelte";
    import * as Button from "$lib/ui/Components/Button";

    interface Props {
        children: Snippet;
        onclick: (((e: Event) => void) | ((e: Event) => Promise<void>)),
        [attribute: string]: unknown;
    }

    let {
        children,
        onclick,
        ...attributes
    }: Props = $props();

    const onClickWrapper = async (e: Event) => {
        await onclick(e);
    }
</script>

<Button.Action
    type="button"
    onclick={onClickWrapper}
    {...attributes}
>
    {@render children()}
</Button.Action>
