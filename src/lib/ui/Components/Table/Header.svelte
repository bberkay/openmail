<script lang="ts">
    import { type Snippet } from "svelte";
    import { combine } from "$lib/utils";

    interface Props {
        children: Snippet
        [attribute: string]: unknown;
    }

    let {
        children,
        ...attributes
    }: Props  = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<thead
    class={combine("thead", additionalClass)}
    {...restAttributes}
>
    {@render children()}
</thead>

<style>
    :global {
        .thead{
            opacity: 1; /* temporary for prevent empty ruleset warning */
        }
    }
</style>
