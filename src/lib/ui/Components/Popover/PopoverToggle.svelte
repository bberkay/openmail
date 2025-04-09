<script lang="ts">
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
    class={combine("popover-toggle-container", additionalClass)}
    {...restAttributes}
>
    <span style="display:none;">#separator#</span>
    {@render children()}
</div>
