<script lang="ts">
    import type { Snippet } from "svelte";
    import * as Button from "$lib/ui/Elements/Button";

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
</script>

<Button.Basic
    type="button"
    {onclick}
    {...attributes}
>
    {@render children()}

</Button.Basic>
