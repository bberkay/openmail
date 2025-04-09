<script lang="ts">
    import { TOGGLE_TEXT_SEPARATOR } from "$lib/constants";
    import { combine } from "$lib/utils";
    import type { Snippet } from "svelte";

    interface Props {
        children: Snippet;
        [attribute: string]: unknown;
    }

    let { children, ...attributes }: Props = $props();

    const {
        class: additionalClass,
        ...restAttributes
    } = attributes;
</script>

<div
    role="button"
    tabindex="0"
    class={combine("dropdown-toggle-container", additionalClass)}
    {...restAttributes}
>
    <span style="display:none;">{TOGGLE_TEXT_SEPARATOR}</span>
    {@render children()}
</div>
