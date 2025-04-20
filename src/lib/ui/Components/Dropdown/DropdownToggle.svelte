<script lang="ts">
    import { combine, getToggleTextSeparator } from "$lib/utils";
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
    <span style="display:none;">{getToggleTextSeparator()}</span>
    {@render children()}
</div>
